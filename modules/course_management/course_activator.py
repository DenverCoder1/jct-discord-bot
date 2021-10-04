import discord
from discord.utils import get
from discord_slash.context import SlashContext
import config
from modules.course_management.util import sort_courses
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj, get_id


async def activate_course(ctx: SlashContext, channel_id: int):
	"""Move a course from the inactive courses category to the active one."""
	channel = discord.utils.get(config.guild().text_channels, id=channel_id)
	if not channel.category_id == get_id("INACTIVE_COURSES_CATEGORY"):
		raise FriendlyError(
			"You can only activate a course which is in the inactive courses category.",
			ctx,
			ctx.author,
		)
	category = get_discord_obj(config.guild().categories, "ACTIVE_COURSES_CATEGORY")
	channel.edit(category=category)
	sort_courses(category)