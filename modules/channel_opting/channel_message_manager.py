from typing import List, Optional
from utils.utils import one
from database.channel_message import ChannelMessage
import discord


class ChannelMessageManager:
	def __init__(self, host_channel: discord.TextChannel, emoji: str):
		self.__host_channel = host_channel
		self.__emoji = emoji

	async def process_reaction(
		self,
		reaction: discord.RawReactionActionEvent,
		channel_messages: List[ChannelMessage],
	):
		if reaction.emoji.name == self.__emoji:
			try:
				channel_message = one(
					cm
					for cm in channel_messages
					if cm.message_id == reaction.message_id
				)
				allowed: Optional[bool]
				if reaction.event_type == "REACTION_ADD":
					member = reaction.member
					allowed = False
				else:
					member = discord.utils.get(
						self.__host_channel.members, id=reaction.user_id
					)
					allowed = None
				if not member or member.bot:
					return
				await channel_message.referenced_channel.set_permissions(
					member, view_channel=allowed
				)
			except StopIteration:
				pass

	async def create_channel_message(
		self, channel_messages: List[ChannelMessage], channel: discord.abc.GuildChannel
	):
		if not isinstance(channel, discord.TextChannel):
			return
		message = await self.__send_channel_message(channel)
		channel_messages.append(
			ChannelMessage.add_to_database(
				message.id, channel.id, self.__host_channel.id
			)
		)

	async def delete_channel_message(
		self, channel_messages: List[ChannelMessage], channel: discord.abc.GuildChannel
	):
		if not isinstance(channel, discord.TextChannel):
			return
		try:
			channel_message = one(
				cm for cm in channel_messages if cm.referenced_channel == channel
			)
			await channel_message.message.delete()
			channel_message.delete_from_database()
			channel_messages.remove(channel_message)
		except StopIteration:
			pass

	async def __send_channel_message(
		self, channel: discord.TextChannel
	) -> discord.Message:
		embed = discord.Embed(
			title=channel.name.replace("-", " ").title(),
			description=channel.mention,
			colour=discord.Colour.dark_purple(),
		)
		embed.set_footer(text=f"Click {self.__emoji} to opt out of this channel.")
		message = await self.__host_channel.send(embed=embed)
		await message.add_reaction(self.__emoji)
		return message
