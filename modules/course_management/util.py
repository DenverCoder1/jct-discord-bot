from typing import Union, overload
import discord
import config
from utils.utils import get_id


@overload
def is_course(channel_id: int, /) -> bool:
	...


@overload
def is_course(channel: discord.TextChannel, /) -> bool:
	...


def is_course(arg1: Union[int, discord.TextChannel]) -> bool:
	channel = (
		discord.utils.get(config.guild().text_channels, id=arg1)
		if isinstance(arg1, int)
		else arg1
	)
	return channel is not None and channel.category_id in {
		get_id("ACTIVE_COURSES_CATEGORY"),
		get_id("INACTIVE_COURSES_CATEGORY"),
	}


async def sort_courses(category: discord.CategoryChannel) -> None:
	"""Sort the courses in the given category alphabetically.

	Args:
		category (CategoryChannel): The category to sort (should be either the active or inactive courses category).
	"""
	pass  # TODO: Implement this
