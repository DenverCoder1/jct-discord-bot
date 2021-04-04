import discord
import config
from functools import cache
from typing import Iterable


class Campus:
	def __init__(self, id: int, name: str, channel_id: int):
		self.id = id
		self.name = name
		self.channel_id = channel_id

	@cache
	def channel(self) -> discord.TextChannel:
		return discord.utils.get(config.guild().text_channels, id=self.channel_id)

	@staticmethod
	def get_campus(campus_id: int) -> "Campus":
		"""Fetch a single campus from the database with the specified id."""
		query = config.sql_fetcher.fetch(
			"database", "campus", "queries", "get_campus.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"campus_id": campus_id})
				return Campus(*cursor.fetchone())

	@staticmethod
	def get_campuses() -> Iterable["Campus"]:
		"""Fetch a list of campuses from the database."""
		query = config.sql_fetcher.fetch(
			"database", "campus", "queries", "get_campuses.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [Campus(*tup) for tup in cursor.fetchall()]