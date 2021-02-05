import discord
import psycopg2.extensions as sql
from typing import Iterable
from .class_role_error import ClassRoleError
from .class_parse_error import ClassParseError
from utils.sql_fetcher import SqlFetcher


class CalendarFinder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def get_calendar_id(self, grad_year: int, campus: str) -> str:
		"""Searches the database the calendar id for a given graduation year and campus"""
		query = self.sql_fetcher["search_calendar.sql"]
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"grad_year": grad_year, "campus": campus})
				row = cursor.fetchone()
		return row[0] if row is not None else None

	def get_class_roles(self, member: discord.Member) -> Iterable[tuple]:
		"""Returns a list of (grad_year, campus) pairs found in a member's roles"""
		roles = member.roles
		class_roles = []
		for role in roles:
			try:
				grad_year, campus = self.extract_year_and_campus(role.name)
				class_roles += [(grad_year, campus)]
			except ClassParseError:
				continue
		return class_roles

	def get_class_info_from_role(self, member: discord.Member) -> tuple:
		"""Returns the grad_year and campus for a member who has only one class role"""
		class_roles = self.get_class_roles(member)
		if len(class_roles) > 1:
			raise ClassRoleError(
				"You must specify which calendar to add to since you have multiple"
				" class roles."
			)
		elif len(class_roles) == 0:
			raise ClassRoleError("Could not find your class role.")
		return class_roles[0]

	def extract_year_and_campus(self, input: str):
		"""Extract campus name and graduation year from input text"""
		# parse graduation year in input
		digits = "".join(c for c in input if c.isdigit())
		if len(digits) == 4 and digits[:2] == "20":  # TODO: fix in 22nd century
			grad_year = int(digits)
		else:
			raise ClassParseError("Could not parse graduation year")
		# parse campus name in input
		if "lev" in input.lower():
			campus = "Lev"
		elif "tal" in input.lower():
			campus = "Tal"
		else:
			raise ClassParseError("Could not parse campus name")
		return grad_year, campus