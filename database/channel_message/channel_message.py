from typing import Iterable
import discord
import config
from functools import cached_property, cache
from database import sql_fetcher


class ChannelMessage:
	"""Represents a message which users can react to to join or leave a channel."""

	def __init__(
		self, message_id: int, referenced_channel_id: int, host_channel_id: int
	):
		self.__message_id = message_id
		self.__referenced_channel_id = referenced_channel_id
		self.__host_channel_id = host_channel_id

	@cached_property
	async def message(self) -> discord.Message:
		"""The message that controls another channel by reacting to it."""
		return await self.__host_channel().fetch_message(self.__message_id)

	@cached_property
	def referenced_channel(self) -> discord.TextChannel:
		"""The channel that this message controls."""
		return self.__get_channel(self.__referenced_channel_id)

	@cache
	def __host_channel(self) -> discord.TextChannel:
		return self.__get_channel(self.__host_channel_id)

	@staticmethod
	def __get_channel(cls, channel_id: int) -> discord.TextChannel:
		return discord.utils.get(config.guild().text_channels, id=channel_id)

	@classmethod
	def get_channel_messages(cls) -> Iterable["ChannelMessage"]:
		query = sql_fetcher.fetch(
			"database", "channel_messages", "queries", "get_channel_messages.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [cls(*tup) for tup in cursor.fetchall()]