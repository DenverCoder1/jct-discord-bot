import discord
import config
from discord_slash.context import SlashContext
from modules.course_management.util import is_course
from ..error.friendly_error import FriendlyError
from database import sql_fetcher


async def delete_course(ctx: SlashContext, channel: discord.TextChannel):
	await __delete_channel(ctx, channel)
	__delete_from_database(channel.id)


async def __delete_channel(ctx: SlashContext, channel: discord.TextChannel):
	if is_course(channel):
		await channel.delete()
	else:
		raise FriendlyError(
			"You must provide a channel in the (active or inactive) courses category.",
			ctx,
			ctx.author,
		)


def __delete_from_database(channel_id: int):
	query = sql_fetcher.fetch(
		"modules", "course_management", "queries", "delete_course.sql"
	)
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(query, {"channel_id": channel_id})