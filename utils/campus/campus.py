import config
from typing import Iterable


class Campus:
	def __init__(self, id: int, name: str):
		self.id = id
		self.name = name

	sql_fetcher = config.sql_fetcher

	@staticmethod
	def get_campuses() -> Iterable["Campus"]:
		"""Fetch a list of campuses from the database"""
		query = Campus.sql_fetcher.fetch(
			"utils", "campus", "queries", "get_campuses.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [Campus(*tup) for tup in cursor.fetchall()]