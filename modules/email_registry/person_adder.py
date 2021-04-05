from database.person.person import Person
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
		channel_mentions: Iterable[str],
		categoriser: Categoriser,
	) -> Person:
		query = self.sql_fetcher.fetch(
			"modules", "email_registry", "queries", "add_person.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query, {"name": name.capitalize(), "surname": surname.capitalize()}
				)
				person_id = cursor.fetchone()[0]
		categoriser.categorise_person(person_id, channel_mentions)
		return Person.get_person(person_id)
