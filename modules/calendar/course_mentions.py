import discord
from discord.ext import commands
import psycopg2.extensions as sql
from typing import Iterable
from utils.sql_fetcher import SqlFetcher


class CourseMentions:
	def __init__(
		self, conn: sql.connection, sql_fetcher: SqlFetcher, bot: commands.Bot
	) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher
		self.bot = bot

	def get_channel_full_name(self, channel: str) -> str:
		"""Searches the database for the course name given the channel id"""
		query = self.sql_fetcher["search_category_name.sql"]
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"channel": channel})
				row = cursor.fetchone()
		if row is not None:
			# return full matched category name
			return row[0]
		else:
			# return the channel name instead
			ch = self.bot.get_channel(int(channel))
			return ch.name if ch is not None else None

	def get_channel_names_from_label(self, label: str) -> Iterable[str]:
		return []