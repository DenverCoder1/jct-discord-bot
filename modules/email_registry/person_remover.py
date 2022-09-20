from typing import Optional

import nextcord
from nextcord.channel import TextChannel
from nextcord.ext import commands

from database import sql
from database.person import Person
from modules.email_registry.person_finder import search_one


async def remove_person(
    interaction: nextcord.Interaction[commands.Bot],
    name: Optional[str] = None,
    channel: Optional[TextChannel] = None,
    email: Optional[str] = None,
) -> Person:
    person = await search_one(interaction, name, channel, email)
    await sql.delete("people", id=person.id)
    return person
