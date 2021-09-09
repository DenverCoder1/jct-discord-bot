from .channel_message_manager import ChannelMessageManager
from utils.utils import get_discord_obj
from database.channel_message import ChannelMessage
from discord.ext import commands
import discord
import config


class ChannelOptingCog(commands.Cog):
	"""Allows users to opt in/out of channels."""

	def __init__(self):
		self.__emoji = "❌"
		self.__channel_messages = list(ChannelMessage.get_channel_messages())
		self.__manager = None

	@commands.Cog.listener()
	async def on_ready(self):
		# skip if this function has already run
		if self.__manager is not None:
			return
		self.__manager = ChannelMessageManager(
			get_discord_obj(config.guild().text_channels, "CHANNEL_DIRECTORY_CHANNEL"),
			self.__emoji,
		)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
		await self.__manager.process_reaction(reaction, self.__channel_messages)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
		await self.__manager.process_reaction(reaction, self.__channel_messages)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
		if channel.guild != config.guild():
			return
		await self.__manager.create_channel_message(self.__channel_messages, channel)

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
		if channel.guild != config.guild():
			return
		await self.__manager.delete_channel_message(self.__channel_messages, channel)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(ChannelOptingCog())
