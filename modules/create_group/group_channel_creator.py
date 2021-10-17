from typing import Iterable
from utils import utils
import config
import discord


async def create_group_channel(
	name: str, roles: Iterable[discord.Role], description: str = ""
) -> discord.TextChannel:
	overwrites = {
		config.guild().default_role: discord.PermissionOverwrite(view_channel=False)
	}
	for role in roles:
		overwrites[role] = discord.PermissionOverwrite(view_channel=True)

	category = utils.get_discord_obj(config.guild().categories, "CLASS_CHAT_CATEGORY")
	return await category.create_text_channel(
		name=name,
		overwrites=overwrites,
		position=len(category.channels) + category.channels[0].position,
		topic=description,
	)