import discord
import config
from typing import Iterable


class Campus:
	def __init__(self, id: int, name: str, channel_id: int):
		self.id = id
		self.name = name
		self.channel_id = channel_id
		self.channel = None

	def campus_channel(self) -> discord.TextChannel:
		if self.channel is None:
			self.channel = discord.utils.get(
				config.guild.text_channels, id=self.channel_id
			)
		return self.channel

	sql_fetcher = config.sql_fetcher

	@staticmethod
	def get_campuses() -> Iterable["Campus"]:
		"""Fetch a list of campuses from the database"""
		query = Campus.sql_fetcher.fetch(
			"utils", "campus", "queries", "get_campuses.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [Campus(*tup) for tup in cursor.fetchall()]