from typing import Iterable
import psycopg2.extensions as sql
import discord
from modules.email_registry.sql_path import sql_path


class Categoriser:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn

	def categorise_person(
		self, person_id: int, channels: Iterable[discord.TextChannel]
	) -> None:
		query = open(sql_path("categorise_person.sql"), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				for channel in channels:
					cursor.execute(
						query, {"person_id": person_id, "channel_id": channel.id}
					)
