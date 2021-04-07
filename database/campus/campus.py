import discord
import config
from functools import cached_property
from typing import Iterable
from database import sql_fetcher


class Campus:
	def __init__(self, id: int, name: str, channel_id: int):
		self.__id = id
		self.__name = name
		self.__channel_id = channel_id

	@property
	def id(self) -> int:
		"""The ID of the campus as stored in the database."""
		return self.__id

	@property
	def name(self) -> str:
		"""The name of the Campus. (eg Lev)"""
		return self.__name

	@cached_property
	def channel(self) -> discord.TextChannel:
		"""The channel associated with this Campus."""
		channel = discord.utils.get(config.guild().text_channels, id=self.__channel_id)
		assert channel is not None
		return channel

	@classmethod
	def get_campus(cls, campus_id: int) -> "Campus":
		"""Fetch a single campus from the database with the specified id."""
		query = sql_fetcher.fetch("database", "campus", "queries", "get_campus.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"campus_id": campus_id})
				return cls(*cursor.fetchone())

	@classmethod
	def get_campuses(cls) -> Iterable["Campus"]:
		"""Fetch a list of campuses from the database."""
		query = sql_fetcher.fetch("database", "campus", "queries", "get_campuses.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [cls(*tup) for tup in cursor.fetchall()]

	def __eq__(self, other):
		"""Compares them by ID"""
		if isinstance(other, self.__class__):
			return self.__id == other.__id
		return False

	def __hash__(self):
		return hash(self.__id)