import nextcord
import config
from modules.course_management.util import (
	sort_single_course,
	ACTIVE_COURSES_CATEGORY,
	INACTIVE_COURSES_CATEGORY,
)
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj, get_id
from nextcord.ext import commands


async def activate_course(
	interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel
):
	"""Move a course from the inactive courses category to the active one."""
	await __move_course(interaction, channel, active=True)


async def deactivate_course(
	interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel
):
	"""Move a course from the active courses category to the inactive one."""
	await __move_course(interaction, channel, active=False)


async def deactivate_all_courses(interaction: nextcord.Interaction[commands.Bot]):
	"""Move all active courses from the active courses to the inactive one."""
	category: nextcord.CategoryChannel = get_discord_obj(
		config.guild().categories, ACTIVE_COURSES_CATEGORY
	)
	for channel in category.text_channels:
		await deactivate_course(interaction, channel)


async def __move_course(
	interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel, active: bool
):
	source_label = INACTIVE_COURSES_CATEGORY if active else ACTIVE_COURSES_CATEGORY
	target_label = ACTIVE_COURSES_CATEGORY if active else INACTIVE_COURSES_CATEGORY
	if not channel.category_id == get_id(source_label):
		raise FriendlyError(
			f"You can only {'activate' if active else 'deactivate'} a course which is"
			f" in the {'inactive' if active else 'active'} courses category",
			interaction,
			interaction.user,
		)
	category = get_discord_obj(config.guild().categories, target_label)
	await channel.edit(category=category)
	await sort_single_course(channel)