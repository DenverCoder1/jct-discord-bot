from database.campus.campus import Campus
from typing import Iterable
from utils.sql_fetcher import SqlFetcher
from modules.create_group.new_group import NewGroup
import psycopg2.extensions as sql


class groups_creator:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher):
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	async def create_groups(self, year: int) -> Iterable[NewGroup]:
		groups = [
			NewGroup(campus, year, self.conn, self.sql_fetcher)
			for campus in Campus.get_campuses()
		]
		for new_group in groups:
			await new_group.add_to_system()
		return groups
