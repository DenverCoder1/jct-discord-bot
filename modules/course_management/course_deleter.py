import discord
import config
from discord_slash.context import SlashContext
from ..error.friendly_error import FriendlyError
from utils.utils import get_discord_obj
from database import sql_fetcher


async def delete_course(ctx: SlashContext, channel_id: int):
	await __delete_channel(ctx, channel_id)
	__delete_from_database(channel_id)


async def __delete_channel(ctx: SlashContext, channel_id: int):
	# find courses category
	category = get_discord_obj(config.guild().categories, "COURSES_CATEGORY")
	channel = discord.utils.get(category.text_channels, id=channel_id)
	if channel:
		await channel.delete()
	else:
		raise FriendlyError(
			"You must provide a channel in the courses category.", ctx, ctx.author
		)


def __delete_from_database(channel_id: int):
	query = sql_fetcher.fetch(
		"modules", "course_management", "queries", "delete_course.sql"
	)
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(query, {"channel_id": channel_id})