from modules.email_registry.sql_path import sql_path
from modules.email_registry.weighted_set import WeightedSet
from typing import Iterable, Set, Optional
from modules.email_registry.person import Person
import discord
import psycopg2.extensions as sql
from modules.error.friendly_error import FriendlyError
import config


class PersonFinder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn
		self.search_weights = {
			"keyword": 1,
			"curr_channel": 1,
			"mentioned_channel": 2,
			"mentioned_person": 3,
		}

	def search(
		self,
		query: Iterable[str],
		mentioned_channels: Iterable[discord.TextChannel],
		curr_channel: discord.TextChannel,
		mentioned_members: Iterable[discord.Member],
	) -> Set[Person]:
		"""returns a list of people who best match the query"""
		weights = WeightedSet()

		# add all people found by mention of the channel of a category they belong to
		for channel in mentioned_channels:
			for person_id in self.__search_channel(channel.id):
				weights[person_id] += self.search_weights["mentioned_channel"]

		# add the people belonging to the category of the current channel (if any)
		for person_id in self.__search_channel(curr_channel.id) or []:
			weights[person_id] += self.search_weights["curr_channel"]

		# add the person found (if any) by mention of their discord account
		for member in mentioned_members:
			person_id = self.__search_member(member.id)
			if person_id is not None:
				weights[person_id] += self.search_weights["mentioned_person"]

		# add all people whose name/course match the search query
		for keyword in query:
			for person_id in self.__search_kw(keyword):
				weights[person_id] += self.search_weights["keyword"]

		people = self.__get_people(weights.heaviest_items())
		return people

	def search_one(
		self,
		query: Iterable[str],
		mentioned_channels: Iterable[discord.TextChannel],
		curr_channel: discord.TextChannel,
		mentioned_members: Iterable[discord.Member],
	) -> Person:
		"""returns a single person who best match the query, or raise a FriendlyError if it couldn't find exactly one."""
		people = self.search(query, mentioned_channels, curr_channel, mentioned_members)
		if not people:
			raise FriendlyError(
				"Unable to find someone who matches your query. Check your spelling or"
				" try a different query. If you still can't find them, You can add"
				f" them with `{config.prefix}addperson`.",
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

	def __search_channel(self, id: int) -> Set[int]:
		"""searches the database for a channel id and returns the IDs of the people who belong to its category"""
		query = open(sql_path("search_channel.sql"), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"channel_id": id})
				ids = {row[0] for row in cursor.fetchall()}
		return ids

	def __search_member(self, id: int) -> Optional[int]:
		"""searches the database for a person's id and returns the IDs of the people who match it"""
		query = open(sql_path("search_member.sql"), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				row = cursor.execute(query, {"member_id": id}).fetchone()
		return row[0] if row is not None else None

	def __search_kw(self, keyword: str) -> Set[int]:
		"""searches the database for a single keyword and returns the IDs of the people who match it"""
		query = open(sql_path("search_kw.sql"), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"kw": keyword})
				ids = {row[0] for row in cursor.fetchall()}
		return ids

	def __get_people(self, ids: Iterable[int]) -> Set[Person]:
		"""searches the database for a person with a given id and returns a Person object"""
		if not ids:
			return set()
		query = open(sql_path("get_people.sql"), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"ids": tuple(ids)})
				people = {
					Person(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()
				}
		return people