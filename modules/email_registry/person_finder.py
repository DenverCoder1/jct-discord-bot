import discord
import config
import psycopg2.extensions as sql
from typing import Iterable, Set, Optional
from modules.email_registry.weighted_set import WeightedSet
from modules.email_registry.person import Person
from modules.error.friendly_error import FriendlyError
from utils.sql_fetcher import SqlFetcher


class PersonFinder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.search_weights = {
			"word": 2,
			"channel": 1,
		}
		self.sql_fetcher = sql_fetcher

	def search(
		self, name: str = None, channel: discord.TextChannel = None
	) -> Set[Person]:
		"""returns a list of people who best match the name and channel"""
		weights = WeightedSet()

		# add the people belonging to the category of the given channel (if any)
		if channel:
			for person_id in self.__search_channel(channel.id):
				weights[person_id] += self.search_weights["channel"]

		# search their name
		if name:
			for word in name.split():
				for person_id in self.__search_by_name(word):
					weights[person_id] += self.search_weights["word"]

		people = self.get_people(weights.heaviest_items())
		return people

	def search_one(
		self, query: Iterable[str], curr_channel: discord.TextChannel,
	) -> Person:
		"""returns a single person who best match the query, or raise a FriendlyError if it couldn't find exactly one."""
		people = self.search(" ".join(query), curr_channel)
		if not people:
			raise FriendlyError(
				f'Unable to find someone who matches "{" ".join(query)}". Check your'
				" spelling or try a different query. If you still can't find them,"
				f" You can add them with `{config.prefix}addperson`.",
				curr_channel,
			)
		if len(people) > 1:
			raise FriendlyError(
				"I cannot accurately determine which of these people you're"
				" referring to. Please provide a more specific query.\n"
				+ ", ".join(person.name for person in people),
				curr_channel,
			)
		return next(iter(people))

	def get_people(self, ids: Iterable[int]) -> Set[Person]:
		"""searches the database for a person with a given id and returns a Person object"""
		if not ids:
			return set()
		query = self.sql_fetcher.fetch(
			"modules", "email_registry", "queries", "get_people.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"ids": tuple(ids)})
				people = {
					Person(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()
				}
		return people

	def __search_channel(self, id: int) -> Set[int]:
		"""searches the database for a channel id and returns the IDs of the people who belong to its category"""
		query = self.sql_fetcher.fetch(
			"modules", "email_registry", "queries", "search_channel.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"channel_id": id})
				ids = {row[0] for row in cursor.fetchall()}
		return ids or {}

	def __search_by_name(self, word: str) -> Set[int]:
		"""searches the database for a single keyword and returns the IDs of the people who match it"""
		query = self.sql_fetcher.fetch(
			"modules", "email_registry", "queries", "search_by_name.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"word": word})
				ids = {row[0] for row in cursor.fetchall()}
		return ids or {}
