from database.campus.campus import Campus
from typing import Iterable
from modules.create_group.new_group import NewGroup
import psycopg2.extensions as sql


class groups_creator:
	def __init__(self, conn: sql.connection):
		self.conn = conn

	async def create_groups(self, year: int) -> Iterable[NewGroup]:
		groups = [NewGroup(campus, year, self.conn) for campus in Campus.get_campuses()]
		for new_group in groups:
			await new_group.add_to_system()
		return groups
