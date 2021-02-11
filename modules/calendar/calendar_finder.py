from .calendar import Calendar
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
		if row is not None:
			return row[0]
		else:
			raise ClassRoleError(f"Could not find a calendar for {campus} {grad_year}.")

	def get_calendar(self, member: discord.Member, text: str = None) -> Calendar:
		# get calendar specified in arguments
		try:
			if text is not None:
				return self.__calendar_from_str(member, text)
		except ClassRoleError as error:
			raise error
		except ClassParseError as error:
			pass
		# get calendar from user's roles
		try:
			return self.__calendar_from_role(member)
		except (ClassRoleError, ClassParseError) as error:
			raise error

	def __calendar_from_str(self, member: discord.Member, text: str) -> Calendar:
		try:
			# parse text for grad_year and campus
			grad_year, campus = self.__extract_year_and_campus(text)
			# check that specified calendar is one of the user's roles
			if (grad_year, campus) not in self.__get_class_roles(member):
				raise ClassRoleError(
					"You don't have the required role to access the requested calendar."
				)
			# get and return calendar info
			return Calendar(
				id=self.get_calendar_id(grad_year, campus),
				name=f"{campus} {grad_year}",
			)
		except (ClassRoleError, ClassParseError) as error:
			raise error

	def __calendar_from_role(self, member: discord.Member) -> Calendar:
		try:
			# get grad_year and campus for member
			grad_year, campus = self.__get_year_campus_from_role(member)
			# get and return calendar info
			return Calendar(
				id=self.get_calendar_id(grad_year, campus),
				name=f"{campus} {grad_year}",
			)
		except (ClassRoleError, ClassParseError) as error:
			raise error

	def __get_class_roles(self, member: discord.Member) -> Iterable[tuple]:
		"""Returns a list of (grad_year, campus) pairs found in a member's roles"""
		roles = member.roles
		class_roles = []
		for role in roles:
			try:
				grad_year, campus = self.__extract_year_and_campus(role.name)
				class_roles += [(grad_year, campus)]
			except ClassParseError:
				continue
		return class_roles

	def __extract_year_and_campus(self, text: str):
		"""Extract campus name and graduation year from input text"""
		# parse graduation year in text
		digits = "".join(c for c in text if c.isdigit())
		if len(digits) == 4 and digits[:2] == "20":  # TODO: fix in 22nd century
			grad_year = int(digits)
		else:
			raise ClassParseError("Could not parse graduation year")
		# parse campus name in text
		if "lev" in text.lower():
			campus = "Lev"
		elif "tal" in text.lower():
			campus = "Tal"
		else:
			raise ClassParseError("Could not parse campus name")
		return grad_year, campus

	def __get_year_campus_from_role(self, member: discord.Member) -> tuple:
		"""Returns the grad_year and campus for a member who has only one class role"""
		class_roles = self.__get_class_roles(member)
		if len(class_roles) > 1:
			raise ClassRoleError(
				"You must specify which calendar since you have multiple class roles."
			)
		elif len(class_roles) == 0:
			raise ClassRoleError("Could not find your class role.")
		return class_roles[0]