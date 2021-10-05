import discord
from discord_slash.context import SlashContext
import config
from modules.course_management.util import sort_single_course
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj, get_id


ACTIVE_COURSES_CATEGORY = "ACTIVE_COURSES_CATEGORY"
INACTIVE_COURSES_CATEGORY = "INACTIVE_COURSES_CATEGORY"


async def activate_course(ctx: SlashContext, channel: discord.TextChannel):
	"""Move a course from the inactive courses category to the active one."""
	await __move_course(ctx, channel, active=True)


async def deactivate_course(ctx: SlashContext, channel: discord.TextChannel):
	"""Move a course from the active courses category to the inactive one."""
	await __move_course(ctx, channel, active=False)


async def deactivate_all_courses(ctx: SlashContext):
	"""Move all active courses from the active courses to the inactive one."""
	category: discord.CategoryChannel = get_discord_obj(
		config.guild().categories, ACTIVE_COURSES_CATEGORY
	)
	for channel in category.text_channels:
		await deactivate_course(ctx, channel)


async def __move_course(ctx: SlashContext, channel: discord.TextChannel, active: bool):
	source_label = INACTIVE_COURSES_CATEGORY if active else ACTIVE_COURSES_CATEGORY
	target_label = ACTIVE_COURSES_CATEGORY if active else INACTIVE_COURSES_CATEGORY
	if not channel.category_id == get_id(source_label):
		raise FriendlyError(
			f"You can only {'activate' if active else 'deactivate'} a course which is"
			f" in the {'active' if active else 'inactive'} courses category",
			ctx,
			ctx.author,
		)
	category = get_discord_obj(config.guild().categories, target_label)
	await channel.edit(category=category)
	await sort_single_course(channel)