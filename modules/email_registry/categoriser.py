from typing import Iterable
from discord_slash.context import SlashContext
from ..error.friendly_error import FriendlyError
from database.person import Person
from database import sql_fetcher
from utils.mention import decode_channel_mention
import config


def categorise_person(
	ctx: SlashContext, person_id: int, channel_mentions: Iterable[str]
) -> Person:
	"""Adds the person to the categories linked to the channels mentioned. Returns the updated person."""
	return __add_remove_categories(
		ctx, "categorise_person.sql", person_id, channel_mentions
	)


def decategorise_person(
	ctx: SlashContext, person_id: int, channel_mentions: Iterable[str]
) -> Person:
	"""Removes the person from the categories linked to the channels mentioned. Returns the updated person."""
	return __add_remove_categories(
		ctx, "decategorise_person.sql", person_id, channel_mentions
	)


def __add_remove_categories(
	ctx: SlashContext, sql_file: str, person_id: int, channel_mentions: Iterable[str]
) -> Person:
	query = sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
	with config.conn as conn:
		with conn.cursor() as cursor:
			for channel in channel_mentions:
				channel_id = decode_channel_mention(channel)
				if channel_id is None:
					raise FriendlyError(
						f'Expected a channel mention in place of "{channel}".',
						ctx,
						ctx.author,
					)
				cursor.execute(
					query, {"person_id": person_id, "channel_id": channel_id}
				)
			return Person.get_person(person_id)
