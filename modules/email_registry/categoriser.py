from typing import Iterable, Optional, Tuple
from utils.utils import decode_mention
import psycopg2.extensions as sql
from modules.email_registry.sql_path import sql_path


class Categoriser:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn

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
		query = open(sql_path(sql_file), "r").read()
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
