from utils.utils import one
import discord
from discord.channel import TextChannel
from discord_slash.context import SlashContext
import config
import psycopg2.extensions as sql
from typing import Any, Iterable, Set, Optional, Union
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
			"email": 5,
		}
		self.sql_fetcher = sql_fetcher

	def search(
		self, name: str = None, channel: discord.TextChannel = None, email: str = None
	) -> Set[Person]:
		"""returns a list of people who best match the name and channel"""
		weights = WeightedSet()

		# add the people belonging to the category of the given channel (if any)
		if channel:
			for person_id in self.__search_people("search_channel.sql", channel.id):
				weights[person_id] += self.search_weights["channel"]

		# search their name
		if name:
			for word in name.split():
				for person_id in self.__search_people("search_by_name.sql", word):
					weights[person_id] += self.search_weights["word"]

		# add the people who have the email mentioned
		if email:
			for person_id in self.__search_people("search_email.sql", email):
				weights[person_id] += self.search_weights["email"]

		people = self.get_people(weights.heaviest_items())
		return people

	def search_one(
		self,
		sendable: Union[TextChannel, SlashContext],
		name: str = None,
		channel: discord.TextChannel = None,
		email: str = None,
	) -> Person:
		"""
		Returns a single person who best match the query, or raise a FriendlyError if it couldn't find exactly one.

		:param sendable: An object with the send method where friendly errors will be sent to.
		:type sendable: discord.TextChannel | commands.Context | SlashContext
		:param name: The name of the person you want to search for.
		:type name: Optional[str]
		:param channel: A channel the person is linked to.
		:type channel: Optional[discord.TextChannel]
		:param email: The email of the person you want to search for.
		:type email: Optional[str]
		"""
		people = self.search(name, channel, email)
		if not people:
			raise FriendlyError(
				"Unable to find someone who matches your query. Check your"
				" spelling or try a different query. If you still can't find them,"
				f" You can add them with `{config.prefix}addperson`.",
				sendable,
			)
		if len(people) > 1:
			raise FriendlyError(
				"I cannot accurately determine which of these people you're"
				" referring to. Please provide a more specific query.\n"
				+ ", ".join(person.name for person in people),
				sendable,
			)
		return one(people)

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

	def __search_people(self, sql_file: str, param: Any) -> Iterable[Person]:
		"""
		Searches the database using a given SQL file and returns a list of people found.

		:param sql_file: The SQL file name to use for the search. Must contain a only `%(param)s`.
		:param param: The parameter to replace %s with in the sql file
		"""
		query = self.sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"param": param})
				ids = {row[0] for row in cursor.fetchall()}
		return ids or {}