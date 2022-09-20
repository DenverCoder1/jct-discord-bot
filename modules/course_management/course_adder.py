from asyncpg.exceptions import UniqueViolationError
import nextcord
from nextcord.abc import Messageable
import nextcord.utils
import config
from modules.course_management.util import ACTIVE_COURSES_CATEGORY, sort_single_course
from ..email_registry import categoriser
from ..email_registry import person_finder
from ..error.friendly_error import FriendlyError
from typing import Iterable
from utils import embedder
from database import sql, sql_fetcher
from utils.utils import get_discord_obj
from nextcord.ext import commands


async def add_course(
	interaction: nextcord.Interaction[commands.Bot],
	course_name: str,
	professors: Iterable[str],
	channel_name: str,
):
	channel = await __create_channel(interaction, channel_name, course_name)
	await __add_to_database(interaction, channel, course_name)
	await __link_professors(interaction, channel, professors)
	return channel


async def __create_channel(
	interaction: nextcord.Interaction[commands.Bot],
	channel_name: str,
	course_name: str = "",
) -> nextcord.TextChannel:
	# find courses category
	category = get_discord_obj(config.guild().categories, ACTIVE_COURSES_CATEGORY)

	# make sure the channel doesn't already exist
	if nextcord.utils.get(category.text_channels, name=channel_name) is not None:
		raise FriendlyError(
			"this channel already exists. Please try again.",
			interaction,
			interaction.user,
		)

	new_channel = await category.create_text_channel(
		channel_name,
		topic=f"Here you can discuss anything related to the course {course_name}.",
	)
	await sort_single_course(new_channel)
	return new_channel


async def __add_to_database(
	interaction: nextcord.Interaction[commands.Bot],
	channel: nextcord.TextChannel,
	course_name: str,
):
	try:
		await sql.insert(
			"categories", returning="id", name=course_name, channel=channel.id
		)
	except UniqueViolationError as e:
		await channel.delete(
			reason=(
				"The command that created this channel ultimately failed, so it was"
				" deleted."
			)
		)
		raise FriendlyError(
			"A course with this name already exists in the database.",
			description=(
				"If a channel for this is missing, then the existing course"
				" will have to be deleted from the database manually. Ask a"
				" bot dev to do this."
			),
			sender=interaction,
			inner=e,
		)


async def __link_professors(
	interaction: nextcord.Interaction[commands.Bot],
	channel: nextcord.TextChannel,
	professors: Iterable[str],
):
	for professor_name in professors:
		try:
			professor = await person_finder.search_one(interaction, professor_name)
			await categoriser.categorise_person(
				interaction, professor.id, (channel.mention,)
			)
		except FriendlyError:
			await interaction.send(
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
