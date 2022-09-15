from nextcord.channel import TextChannel
from modules.email_registry.person_finder import search_one
from database.person import Person
import nextcord
from typing import Optional
from database import sql


async def remove_person(
	interaction: nextcord.Interaction,
	name: Optional[str] = None,
	channel: Optional[TextChannel] = None,
	email: Optional[str] = None,
) -> Person:
	person = await search_one(interaction, name, channel, email)
	await sql.delete("people", id=person.id)
	return person
