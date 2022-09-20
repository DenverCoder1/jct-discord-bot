from typing import List, Optional
from utils.embedder import build_embed
from utils.utils import one
from database.channel_message import ChannelMessage
import nextcord


class ChannelMessageManager:
	def __init__(self, host_channel: nextcord.TextChannel, emoji: str):
		self.__host_channel = host_channel
		self.__emoji = emoji

	async def process_reaction(
		self, reaction: nextcord.RawReactionActionEvent, channel_messages: List[ChannelMessage],
	):
		if reaction.emoji.name == self.__emoji:
			try:
				channel_message = one(
					cm for cm in channel_messages if cm.message_id == reaction.message_id
				)
				allowed: Optional[bool]
				if reaction.event_type == "REACTION_ADD":
					member = reaction.member
					allowed = False
				else:
					member = nextcord.utils.get(self.__host_channel.members, id=reaction.user_id)
					allowed = None
				if not member or member.bot:
					return
				channel = channel_message.referenced_channel
				assert channel is not None
				await channel.set_permissions(member, view_channel=allowed)
			except StopIteration:
				pass

	async def create_channel_message(
		self, channel_messages: List[ChannelMessage], channel: nextcord.abc.GuildChannel
	):
		if not isinstance(channel, nextcord.TextChannel):
			return
		message = await self.__send_channel_message(channel)
		channel_messages.append(
			await ChannelMessage.add_to_database(message.id, channel.id, self.__host_channel.id)
		)

	async def delete_channel_message(
		self, channel_messages: List[ChannelMessage], channel: nextcord.abc.GuildChannel
	):
		if not isinstance(channel, nextcord.TextChannel):
			return
		try:
			channel_message = one(
				cm for cm in channel_messages if cm.referenced_channel_id == channel.id
			)
			await (await channel_message.message).delete()
			await channel_message.delete_from_database()
			channel_messages.remove(channel_message)
		except StopIteration:
			pass

	async def __send_channel_message(self, channel: nextcord.TextChannel) -> nextcord.Message:
		embed = build_embed(
			title=channel.name.replace("-", " ").title(),
			footer=f"Click {self.__emoji} to opt out of this channel.",
			description=channel.mention,
			colour=nextcord.Colour.dark_purple(),
		)
		message = await self.__host_channel.send(embed=embed)
		await message.add_reaction(self.__emoji)
		return message
