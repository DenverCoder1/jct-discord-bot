from typing import Union
import discord
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from utils.sql_fetcher import SqlFetcher
from utils.utils import is_email
from modules.email_registry.person import Person
import psycopg2.extensions as sql
from psycopg2.errors import UniqueViolation, CheckViolation


class EmailAdder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def add_email(self, person: Person, email: str, ctx: SlashContext) -> None:
		self.__add_remove_email("add_email.sql", person, email, ctx)

	def remove_email(self, person: Person, email: str, ctx: SlashContext) -> None:
		self.__add_remove_email("remove_email.sql", person, email, ctx)

	def __add_remove_email(
		self, sql_file: str, person: Person, email: str, ctx: SlashContext
	) -> None:
		query = self.sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
		with self.conn as conn:
			with conn.cursor() as cursor:
				try:
					cursor.execute(query, {"person_id": person.id, "email": email})
				except UniqueViolation as e:
					raise FriendlyError(
						f"Ignoring request to add {email} to {person.name}; it"
						" is already in the system.",
						sender=ctx,
						inner=e,
					)
				except CheckViolation as e:
					raise FriendlyError(
						f'"{email}" is not a valid email address.', sender=ctx, inner=e,
					)
