import nextcord
import config
from utils.utils import get_discord_obj, get_id


ACTIVE_COURSES_CATEGORY = "ACTIVE_COURSES_CATEGORY"
INACTIVE_COURSES_CATEGORY = "INACTIVE_COURSES_CATEGORY"


def is_course(channel: nextcord.TextChannel) -> bool:
	return channel is not None and channel.category_id in {
		get_id(ACTIVE_COURSES_CATEGORY),
		get_id(INACTIVE_COURSES_CATEGORY),
	}


async def sort_courses() -> None:
	"""Sort the courses in the given category alphabetically."""
	for label in {ACTIVE_COURSES_CATEGORY, INACTIVE_COURSES_CATEGORY}:
		category = get_discord_obj(config.guild().categories, label)
		if not category.text_channels:
			return
		start_position = category.text_channels[0].position
		for i, channel in enumerate(
			sorted(category.text_channels, key=lambda c: c.name)
		):
			await channel.edit(position=start_position + i)


async def sort_single_course(channel: nextcord.TextChannel) -> None:
	"""Reposition a single course within its category. This function assumes that the rest of the categories are in sorted order; if thry aren't, use the alternative function `sort_courses`

	Args:
		channel (nextcord.TextChannel): The channel to sort within its category.
	"""
	assert channel.category is not None
	for other_channel in channel.category.text_channels:
		if other_channel != channel and other_channel.name > channel.name:
			await channel.edit(position=other_channel.position)
			break
