import discord
import psycopg2.extensions as sql
from typing import Iterable
from modules.email_registry.categoriser import Categoriser
from utils.sql_fetcher import SqlFetcher


class PersonAdder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def add_person(
		self,
		name: str,
		surname: str,
		channels: Iterable[discord.TextChannel],
		categoriser: Categoriser,
		member_id: int = None,
	) -> int:
		query = self.sql_fetcher["add_person.sql"]
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query, {"name": name, "surname": surname, "member_id": member_id}
				)
				person_id = cursor.fetchone()[0]
		categoriser.categorise_person(
			person_id, [channel.mention for channel in channels]
		)
		return person_id
