from typing import Iterable
import discord
import psycopg2.extensions as sql
from modules.email_registry.sql_path import sql_path
from modules.email_registry.categoriser import Categoriser


class PersonAdder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn

	def add_person(
		self,
		name: str,
		surname: str,
		channels: Iterable[discord.TextChannel],
		categoriser: Categoriser,
		member_id: int = None,
	):
		cursor = self.conn.cursor()
		query = open(sql_path("add_person.sql"), "r").read()
		cursor.execute(
			query, {"name": name, "surname": surname, "member_id": member_id}
		)
		person_id = cursor.fetchone()[0]
		self.conn.commit()
		cursor.close()
		categoriser.categorise_person(person_id, channels)
