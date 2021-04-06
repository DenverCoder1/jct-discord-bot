import discord
import config
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj
from database import sql_fetcher
import psycopg2.extensions as sql


class CourseDeleter:
	def __init__(self, conn: sql.connection):
		self.conn = conn

	async def delete_course(self, ctx: SlashContext, channel_id: int):
		await self.__delete_channel(ctx, channel_id)
		self.__delete_from_database(channel_id)

	async def __delete_channel(self, ctx: SlashContext, channel_id: int):
		# find courses category
		category = get_discord_obj(config.guild.categories, "COURSES_CATEGORY")
		try:
			await discord.utils.get(category.text_channels, id=channel_id).delete()
		except AttributeError as e:
			raise FriendlyError(
				"You must provide a channel in the courses category.",
				ctx,
				ctx.author,
				e,
			)

	def __delete_from_database(self, channel_id: int):
		query = sql_fetcher.fetch(
			"modules", "course_management", "queries", "delete_course.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"channel_id": channel_id})