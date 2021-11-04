from discord.channel import TextChannel
from modules.email_registry.person_finder import search_one
from discord_slash.context import SlashContext
from database.person import Person
import config
from typing import Optional
from database import sql


async def remove_person(
	ctx: SlashContext,
	name: Optional[str] = None,
	channel: Optional[TextChannel] = None,
	email: Optional[str] = None,
) -> Person:
	person = await search_one(ctx, name, channel, email)
	await sql.delete("people", id=person.id)
	return person
