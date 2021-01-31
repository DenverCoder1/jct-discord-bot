from typing import Iterable, Optional, Tuple
from utils.sql_fetcher import SqlFetcher
from utils.utils import decode_mention
import psycopg2.extensions as sql


class Categoriser:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def categorise_person(
		self, person_id: int, channels: Iterable[str]
	) -> Tuple[bool, Optional[str]]:
		"""Adds the person to the categories linked to the channels mentioned. Returns whether or not it succeeded on the first retrun value, and an error message (or None) as the second value."""
		return self.__add_remove_categories(
			"categorise_person.sql", person_id, channels
		)

	def decategorise_person(
		self, person_id: int, channels: Iterable[str]
	) -> Tuple[bool, Optional[str]]:
		"""Removes the person from the categories linked to the channels mentioned. Returns whether or not it succeeded on the first retrun value, and an error message (or None) as the second value."""
		return self.__add_remove_categories(
			"decategorise_person.sql", person_id, channels
		)

	def __add_remove_categories(
		self, sql_file: str, person_id: int, channels: Iterable[str]
	) -> Tuple[bool, Optional[str]]:
		query = self.sql_fetcher[sql_file]
		with self.conn as conn:
			with conn.cursor() as cursor:
				for channel in channels:
					mention_type, channel_id = decode_mention(channel)
					if mention_type != "channel":
						return (
							False,
							f'Expected a channel mention in place of "{channel}".',
						)
					cursor.execute(
						query, {"person_id": person_id, "channel_id": channel_id}
					)
					return True, None
