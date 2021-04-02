import config
from typing import Iterable


class ClassRole:
	def __init__(self, id: int, name: str, calendar: str):
		self.id = id
		self.name = name
		self.calendar = calendar

	sql_fetcher = config.sql_fetcher

	@staticmethod
	def get_class_roles() -> Iterable["ClassRole"]:
		"""Fetch a list of class roles from the database"""
		query = ClassRole.sql_fetcher.fetch(
			"utils", "class_role", "queries", "get_class_roles.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [ClassRole(*tup) for tup in cursor.fetchall()]