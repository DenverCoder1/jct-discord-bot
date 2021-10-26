from typing import Iterable, Optional
import discord
import config
from functools import cached_property, cache
from database import sql


class ChannelMessage:
	"""Represents a message which users can react to to join or leave a channel."""

	def __init__(
		self, message_id: int, referenced_channel_id: int, host_channel_id: int
	):
		self.__message_id = message_id
		self.__referenced_channel_id = referenced_channel_id
		self.__host_channel_id = host_channel_id

	@property
	def message_id(self) -> int:
		"""The discord ID of the message."""
		return self.__message_id

	@cached_property
	async def message(self) -> discord.Message:
		"""The message that controls another channel by reacting to it."""
		return await self.__host_channel().fetch_message(self.__message_id)

	@cached_property
	def referenced_channel_id(self) -> int:
		"""The ID of the channel that this message controls."""
		return self.__referenced_channel_id

	@cached_property
	def referenced_channel(self) -> Optional[discord.TextChannel]:
		"""The channel that this message controls, or None if the channel has been deleted."""
		return self.__get_channel(self.__referenced_channel_id)

	@cache
	def __host_channel(self) -> discord.TextChannel:
		channel = self.__get_channel(self.__host_channel_id)
		assert channel is not None
		return channel

	@staticmethod
	def __get_channel(channel_id: int) -> Optional[discord.TextChannel]:
		"""
		Returns a channel with the given ID, or None if it doesn't exist or is deleted.
		"""
		channel = discord.utils.get(config.guild().text_channels, id=channel_id)
		return channel

	@classmethod
	async def get_channel_messages(cls) -> Iterable["ChannelMessage"]:
		records = await sql.select.many(
			"channel_messages", ("message", "referenced_channel", "host_channel")
		)
		return [cls(*record) for record in records]

	@classmethod
	async def add_to_database(
		cls, message_id: int, referenced_channel_id: int, host_channel_id: int
	) -> "ChannelMessage":
		await sql.insert(
			"channel_messages",
			message=message_id,
			referenced_channel=referenced_channel_id,
			host_channel=host_channel_id,
		)
		return cls(message_id, referenced_channel_id, host_channel_id)

	async def delete_from_database(self):
		await sql.delete("channel_messages", message=self.message_id)