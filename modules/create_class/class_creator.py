from modules.create_class.campus import Campus
from typing import Iterable
from utils.sql_fetcher import SqlFetcher
from modules.create_class.class import Class
import psycopg2.extensions as sql


class classes_creator:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher):
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	async def create_classes(self, year: int) -> Iterable[Class]:
		# Fetch campuses from the database
		query = self.sql_fetcher["get_campuses.sql"]
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				campuses = [Campus(*tup) for tup in cursor.fetchall()]

		return [Class(campus, year) for campus in campuses]
