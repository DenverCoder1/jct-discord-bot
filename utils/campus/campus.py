import os
import config
from typing import Iterable
from utils.sql_fetcher import SqlFetcher


class Campus:
	def __init__(self, id: int, name: str):
		self.id = id
		self.name = name

	sql_fetcher = SqlFetcher(os.path.join("utils", "campus", "queries"))

	@staticmethod
	def get_campuses() -> Iterable["Campus"]:
		"""Fetch a list of campuses from the database"""
		query = Campus.sql_fetcher["get_campuses.sql"]
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [Campus(*tup) for tup in cursor.fetchall()]