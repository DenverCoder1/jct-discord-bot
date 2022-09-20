from typing import Iterable

import nextcord
from nextcord.ext import commands

from database import sql
from database.person import Person

from . import categoriser


async def add_person(
    name: str,
    surname: str,
    channel_mentions: Iterable[str],
    interaction: nextcord.Interaction[commands.Bot],
) -> Person:
    person_id = await sql.insert(
        "people", returning="id", name=name.capitalize(), surname=surname.capitalize()
    )
    return await categoriser.categorise_person(interaction, person_id, channel_mentions)
