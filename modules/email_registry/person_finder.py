from utils.utils import one
import discord
from discord.channel import TextChannel
from discord_slash.context import SlashContext
import psycopg2.extensions as sql
from typing import Any, Iterable, Optional, Set, Union
from modules.email_registry.weighted_set import WeightedSet
from database.person.person import Person
from modules.error.friendly_error import FriendlyError
from database import sql_fetcher


class PersonFinder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn
		self.search_weights = {
			"word": 2,
			"channel": 1,
			"email": 5,
		}

	def search(
		self,
		name: Optional[str] = None,
		channel: Optional[discord.TextChannel] = None,
		email: Optional[str] = None,
	) -> Set[Person]:
		"""returns a list of people who best match the name and channel"""
		weights = WeightedSet()

		# add the people belonging to the category of the given channel (if any)
		if channel:
			for person in self.__search_people("search_channel.sql", channel.id):
				weights[person] += self.search_weights["channel"]

		# search their name
		if name:
			for word in name.split():
				for person in self.__search_people("search_by_name.sql", word):
					weights[person] += self.search_weights["word"]

		# add the people who have the email mentioned
		if email:
			for person in self.__search_people("search_email.sql", email):
				weights[person] += self.search_weights["email"]

		return weights.heaviest_items()

	def search_one(
		self,
		sender: Union[TextChannel, SlashContext],
		name: Optional[str] = None,
		channel: Optional[discord.TextChannel] = None,
		email: Optional[str] = None,
	) -> Person:
		"""
		Returns a single person who best match the query, or raise a FriendlyError if it couldn't find exactly one.

		:param sender: An object with the send method where friendly errors will be sent to.
		:type sender: discord.TextChannel | commands.Context | SlashContext
		:param name: The name of the person you want to search for (first, last, or both).
		:type name: Optional[str]
		:param channel: A channel the person is linked to.
		:type channel: Optional[discord.TextChannel]
		:param email: The email of the person you want to search for.
		:type email: Optional[str]
		"""
		people = self.search(name, channel, email)
		if not people:
			raise FriendlyError(
				f"Unable to find someone who matches your query. Check your spelling or"
				f" try a different query. If you still can't find them, You can add"
				f" them with `/email person add`.",
				sender,
			)
		if len(people) > 1:
			raise FriendlyError(
				"I cannot accurately determine which of these people you're"
				" referring to. Please provide a more specific query.\n"
				+ ", ".join(person.name for person in people),
				sender,
			)
		return one(people)

	def __search_people(self, sql_file: str, param: Any) -> Iterable[Person]:
		"""
		Searches the database using a given SQL file and returns a list of people found.

		:param sql_file: The SQL file name to use for the search. Must contain a only `%(param)s`.
		:param param: The parameter to replace %s with in the sql file
		"""
		query = sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"param": param})
				ids = {row[0] for row in cursor.fetchall()}
		return {Person.get_person(person_id) for person_id in ids}