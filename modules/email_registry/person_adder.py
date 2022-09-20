from database.person import Person
import nextcord
from typing import Iterable
from . import categoriser
from database import sql
from nextcord.ext import commands


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
