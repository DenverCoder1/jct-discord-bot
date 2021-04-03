from typing import Iterable, Optional, Tuple
from utils.sql_fetcher import SqlFetcher
from utils.mention import decode_channel_mention
import psycopg2.extensions as sql


class Categoriser:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def categorise_person(self, person_id: int, channel_mentions: Iterable[str]) -> str:
		"""Adds the person to the categories linked to the channels mentioned. Returns an error message (string) or an empty string."""
		return self.__add_remove_categories(
			"categorise_person.sql", person_id, channel_mentions
		)

	def decategorise_person(
		self, person_id: int, channel_mentions: Iterable[str]
	) -> str:
		"""Removes the person from the categories linked to the channels mentioned. Returns an error message (string) or an empty string."""
		return self.__add_remove_categories(
			"decategorise_person.sql", person_id, channel_mentions
		)

	def __add_remove_categories(
		self, sql_file: str, person_id: int, channel_mentions: Iterable[str]
	) -> str:
		query = self.sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
		with self.conn as conn:
			with conn.cursor() as cursor:
				for channel in channel_mentions:
					channel_id = decode_channel_mention(channel)
					if channel_id is None:
						return f'Expected a channel mention in place of "{channel}".'
					cursor.execute(
						query, {"person_id": person_id, "channel_id": channel_id}
					)
				return ""
