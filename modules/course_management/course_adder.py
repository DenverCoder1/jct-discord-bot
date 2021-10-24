import discord
from discord.abc import Messageable
import discord.utils
import config
from discord_slash.context import SlashContext
from psycopg2 import errors
from modules.course_management.util import ACTIVE_COURSES_CATEGORY, sort_single_course
from ..email_registry import categoriser
from ..email_registry import person_finder
from ..error.friendly_error import FriendlyError
from typing import Iterable
from utils import embedder
from database import sql_fetcher
from utils.utils import get_discord_obj

UniqueViolation = errors.lookup("23505")


async def add_course(
	ctx: SlashContext, course_name: str, professors: Iterable[str], channel_name: str,
):
	channel = await __create_channel(ctx, channel_name, course_name)
	await __add_to_database(ctx, channel, course_name)
	await __link_professors(ctx, channel, professors)
	return channel


async def __create_channel(
	ctx: SlashContext, channel_name: str, course_name: str = ""
) -> discord.TextChannel:
	# find courses category
	category = get_discord_obj(config.guild().categories, ACTIVE_COURSES_CATEGORY)

	# make sure the channel doesn't already exist
	if discord.utils.get(category.text_channels, name=channel_name) is not None:
		raise FriendlyError(
			"this channel already exists. Please try again.", ctx, ctx.author,
		)

	new_channel = await category.create_text_channel(
		channel_name,
		topic=f"Here you can discuss anything related to the course {course_name}.",
	)
	await sort_single_course(new_channel)
	return new_channel


async def __add_to_database(
	messageable: Messageable, channel: discord.TextChannel, course_name: str
):
	course_query = sql_fetcher.fetch(
		"modules", "course_management", "queries", "add_course.sql"
	)
	with config.conn as conn:
		with conn.cursor() as cursor:
			# add the course to the database
			try:
				cursor.execute(
					course_query,
					{"course_name": course_name, "channel_id": channel.id},
				)
			except UniqueViolation as e:
				await channel.delete(
					reason=(
						"The command that created this channel ultimately failed,"
						" so it was deleted."
					)
				)
				raise FriendlyError(
					"A course with this name already exists in the database.",
					description=(
						"If a channel for this is missing, then the existing course"
						" will have to be deleted from the database manually. Ask a"
						" bot dev to do this."
					),
					messageable=messageable,
					inner=e,
				)


async def __link_professors(
	ctx: SlashContext, channel: discord.TextChannel, professors: Iterable[str],
):
	for professor_name in professors:
		try:
			professor = person_finder.search_one(ctx, professor_name)
			categoriser.categorise_person(ctx, professor.id, (channel.mention,))
		except FriendlyError:
			await ctx.send(
				embed=embedder.embed_warning(
					title=(
						f'Unable to determine who you meant by "{professor_name}".'
						" I will skip linking this professor to the course."
					),
					description=(
						"To link the professor yourself, first add them with"
						" `/email person add` if they're not in the system, then"
						" link them with `/email person link`"
					),
				)
			)
