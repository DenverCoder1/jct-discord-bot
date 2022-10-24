from typing import Iterable

import nextcord

import config
from utils import utils


async def create_group_channel(
    name: str, roles: Iterable[nextcord.Role], description: str = ""
) -> nextcord.TextChannel:
    overwrites = {config.guild().default_role: nextcord.PermissionOverwrite(view_channel=False)}
    for role in roles:
        overwrites[role] = nextcord.PermissionOverwrite(view_channel=True)

    category = utils.get_discord_obj(config.guild().categories, "CLASS_CHAT_CATEGORY")
    return await category.create_text_channel(
        name=name,
        overwrites=overwrites,
        position=len(category.channels) + category.channels[0].position,
        topic=description,
    )
