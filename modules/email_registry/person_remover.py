from discord.channel import TextChannel
from modules.email_registry.person_finder import search_one
from modules.email_registry.email_adder import remove_email
from discord_slash.context import SlashContext
from database.person import Person
import config
from typing import Optional
from database import sql_fetcher


def remove_person(
	ctx: SlashContext,
	name: Optional[str] = None,
	channel: Optional[TextChannel] = None,
	email: Optional[str] = None,
) -> Person:
	person = search_one(ctx, name, channel, email)
	for email in person.emails:
		remove_email(person, email, ctx)
	query = sql_fetcher.fetch(
		"modules", "email_registry", "queries", "remove_person.sql"
	)
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(query, {"id": person.id})
	return person
