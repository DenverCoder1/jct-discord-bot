from typing import Iterable

import nextcord
from nextcord.ext import commands

from database import config as db_config, sql_fetcher
from database.person import Person
from utils.mention import decode_channel_mention

from ..error.friendly_error import FriendlyError


async def categorise_person(
    interaction: nextcord.Interaction[commands.Bot],
    person_id: int,
    channel_mentions: Iterable[str],
) -> Person:
    """Adds the person to the categories linked to the channels mentioned. Returns the updated person."""
    return await __add_remove_categories(
        interaction, "categorise_person.sql", person_id, channel_mentions
    )


async def decategorise_person(
    interaction: nextcord.Interaction[commands.Bot],
    person_id: int,
    channel_mentions: Iterable[str],
) -> Person:
    """Removes the person from the categories linked to the channels mentioned. Returns the updated person."""
    return await __add_remove_categories(
        interaction, "decategorise_person.sql", person_id, channel_mentions
    )


async def __add_remove_categories(
    interaction: nextcord.Interaction[commands.Bot],
    sql_file: str,
    person_id: int,
    channel_mentions: Iterable[str],
) -> Person:
    conn = await db_config.get_connection()
    query = sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
    async with conn.transaction():
        for channel in channel_mentions:
            channel_id = decode_channel_mention(channel)
            if channel_id is None:
                raise FriendlyError(
                    f'Expected a channel mention in place of "{channel}".',
                    interaction,
                    interaction.user,
                )
            await conn.execute(query, person_id, channel_id)
    return await Person.get_person(person_id)
