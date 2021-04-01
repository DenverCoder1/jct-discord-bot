import os
import psycopg2.extensions as sql
import discord
import discord.utils
import config
from discord.ext import commands
from modules.email_registry.categoriser import Categoriser
from modules.email_registry.person_finder import PersonFinder
from modules.error.friendly_error import FriendlyError
from psycopg2.extras import execute_values
from typing import Iterable
from utils import embedder
from utils.sql_fetcher import SqlFetcher
from utils.utils import get_discord_obj


class CourseAdder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher):
		self.conn = conn
		self.sql_fetcher = sql_fetcher
		self.categoriser = Categoriser(conn, sql_fetcher)
		self.finder = PersonFinder(conn, sql_fetcher)

	async def add_course(
		self,
		ctx: commands.Context,
		course_name: str,
		labels: Iterable[str],
		professors: Iterable[str],
		channel_name: str,
	):
		channel = await self.__create_channel(ctx, channel_name)
		self.__add_to_database(channel, course_name, labels)
		await self.__link_professors(ctx, channel, professors)
		return channel

	async def __create_channel(
		self, ctx: commands.Context, channel_name: str
	) -> discord.TextChannel:
		# find courses category
		guild = ctx.guild
		category = get_discord_obj(guild.categories, "COURSES_CATEGORY")

		# make sure the channel doesn't already exist
		if discord.utils.get(category.text_channels, name=channel_name) is not None:
			raise FriendlyError(
				"this channel already exists. Please try again.",
				ctx.channel,
				ctx.author,
			)

		# create the new course channel
		new_channel = await category.create_text_channel(channel_name)

		# find position to insert the new course channel
		position = category.text_channels[-1].position + 1
		for channel in category.text_channels:
			if channel.name > new_channel.name:
				position = channel.position - 1
				break

		# reposition course channel to be in alphabetic order
		# must be done post-creation because channel name may be changed by discord on creation
		await new_channel.edit(position=position)

		return new_channel

	def __add_to_database(
		self, channel: discord.TextChannel, course_name: str, labels: Iterable[str]
	):
		course_query = self.sql_fetcher.fetch(
			os.path.join("modules", "course_management", "queries", "add_course.sql")
		)
		labels_query = self.sql_fetcher.fetch(
			os.path.join("modules", "course_management", "queries", "add_label.sql")
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				# add the course to the database
				cursor.execute(
					course_query, {"course_name": course_name, "channel_id": channel.id}
				)
				# add the labels to the course
				execute_values(
					cursor,
					labels_query,
					argslist=[{"label": label} for label in labels],
					template=f"({cursor.fetchone()[0]}, %(label)s)",
				)

	async def __link_professors(
		self,
		ctx: commands.Context,
		channel: discord.TextChannel,
		professors: Iterable[str],
	):
		for professor in professors:
			professor = professor.strip()
			try:
				professor_id = self.finder.search_one(professor.split(), ctx.channel).id
				self.categoriser.categorise_person(professor_id, (channel.mention,))
			except FriendlyError:
				await ctx.send(
					embed=embedder.embed_warning(
						title=(
							f'Unable to determine who you meant by "{professor}". I'
							" will skip linking this professor to the course."
						),
						description=(
							"To link the professor yourself, first add them with"
							f" `{config.prefix}addperson` if they're not in the"
							f" system, then link them with\n```\n{config.prefix}link"
							f' "{professor}" to #{channel.name}```'
						),
					)
				)
