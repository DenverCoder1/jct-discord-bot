from typing import Literal, Union
import discord
from discord_slash.context import SlashContext
import config
from modules.course_management.util import sort_single_course
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj, get_id


async def activate_course(ctx: SlashContext, channel: discord.TextChannel):
	"""Move a course from the inactive courses category to the active one."""
	await __move_course(ctx, channel, "activate")


async def deactivate_course(ctx: SlashContext, channel: discord.TextChannel):
	"""Move a course from the active categories category to the inactive one."""
	await __move_course(ctx, channel, "deactivate")


async def __move_course(
	ctx: SlashContext,
	channel: discord.TextChannel,
	action: Union[Literal["activate"], Literal["deactivate"]],
):
	source_label, target_label = map(
		lambda prefix: prefix + "ACTIVE_COURSES_CATEGORY",
		("IN", "") if action == "activate" else ("", "IN"),
	)
	if not channel.category_id == get_id(source_label):
		raise FriendlyError(
			f"You can only {action} a course which is in the"
			f" {source_label.lower().replace('_', ' ')}",
			ctx,
			ctx.author,
		)
	category = get_discord_obj(config.guild().categories, target_label)
	await channel.edit(category=category)
	await sort_single_course(channel)