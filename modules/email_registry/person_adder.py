from database.person import Person
import config
from typing import Iterable
from . import categoriser
from database import sql, sql_fetcher


async def add_person(
	name: str, surname: str, channel_mentions: Iterable[str], interaction: nextcord.Interaction,
) -> Person:
	person_id = await sql.insert(
		"people", returning="id", name=name.capitalize(), surname=surname.capitalize()
	)
	return await categoriser.categorise_person(ctx, person_id, channel_mentions)
