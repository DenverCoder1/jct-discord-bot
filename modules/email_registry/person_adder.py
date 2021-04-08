from discord_slash.context import SlashContext
from database.person import Person
import config
from typing import Iterable
from . import categoriser
from database import sql_fetcher


def add_person(
	name: str, surname: str, channel_mentions: Iterable[str], ctx: SlashContext,
) -> Person:
	query = sql_fetcher.fetch("modules", "email_registry", "queries", "add_person.sql")
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(
				query, {"name": name.capitalize(), "surname": surname.capitalize()}
			)
			person_id = cursor.fetchone()[0]
	return categoriser.categorise_person(ctx, person_id, channel_mentions)
