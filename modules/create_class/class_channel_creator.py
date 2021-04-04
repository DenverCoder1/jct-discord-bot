from typing import Iterable
from utils import utils
import config
import discord


class ClassChannelCreator:
	@staticmethod
	async def create_class_channel(name: str, classes: Iterable) -> discord.TextChannel:
		overwrites = {
			config.guild.default_role: discord.PermissionOverwrite(view_channel=False)
		}
		for class_ in classes:
			overwrites[class_.role] = discord.PermissionOverwrite(view_channel=True)

		category = utils.get_discord_obj(config.guild.categories, "CLASS_CHAT_CATEGORY")
		return await category.create_text_channel(
			name=name,
			overwrites=overwrites,
			position=len(category.channels) + category.channels[0].position,
		)