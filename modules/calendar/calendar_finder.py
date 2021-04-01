import os
from .calendar import Calendar
import discord
import psycopg2.extensions as sql
from typing import Iterable
from .class_role_error import ClassRoleError
from .class_parse_error import ClassParseError
from utils.sql_fetcher import SqlFetcher
import re


class CalendarFinder:
	def __init__(self, conn: sql.connection, sql_fetcher: SqlFetcher) -> None:
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	def get_calendar_id(self, grad_year: int, campus: str) -> str:
		"""Searches the database the calendar id for a given graduation year and campus"""
		query = self.sql_fetcher.fetch(
			os.path.join("modules", "calendar", "queries", "search_calendar.sql")
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"grad_year": grad_year, "campus": campus})
				row = cursor.fetchone()
		if row is not None:
			return row[0]
		else:
			raise ClassRoleError(f"Could not find a calendar for {campus} {grad_year}.")

	def get_campus(self, text: str) -> str:
		"""Searches the database the campus matching the user's string"""
		query = self.sql_fetcher.fetch(
			os.path.join("modules", "calendar", "queries", "search_campus.sql")
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"text": text})
				row = cursor.fetchall()
		if row is not None and len(row) == 1:
			return row[0][0]
		else:
			raise ClassRoleError(f"Could not find a matching campus name.")

	def get_calendar(self, member: discord.Member, text: str = None) -> Calendar:
		# get calendar specified in arguments
		try:
			if text:
				return self.__calendar_from_str(member, text)
		except ClassParseError:
			pass
		# get calendar from user's roles
		return self.__calendar_from_role(member)

	def __calendar_from_str(self, member: discord.Member, text: str) -> Calendar:
		# parse text for grad_year and campus
		grad_year, campus = self.__extract_year_and_campus(text)
		# check that specified calendar is one of the user's roles
		if (grad_year, campus) not in self.__get_class_roles(member):
			raise ClassRoleError(
				"You don't have the required role to access the requested calendar."
			)
		# get and return calendar info
		return Calendar(
			id=self.get_calendar_id(grad_year, campus), name=f"{campus} {grad_year}",
		)

	def __calendar_from_role(self, member: discord.Member) -> Calendar:
		# get grad_year and campus for member
		grad_year, campus = self.__get_year_campus_from_role(member)
		# get and return calendar info
		return Calendar(
			id=self.get_calendar_id(grad_year, campus), name=f"{campus} {grad_year}",
		)

	def __get_class_roles(self, member: discord.Member) -> Iterable[tuple]:
		"""Returns a list of (grad_year, campus) pairs found in a member's roles"""
		query = self.sql_fetcher.fetch(
			os.path.join("modules", "calendar", "queries", "get_class_roles.sql")
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query, {"roles": tuple(role.id for role in member.roles)}
				)
				return cursor.fetchall()

	def __extract_year_and_campus(self, text: str):
		"""Extract campus name and graduation year from input text"""
		try:
			# TODO: fix in 22nd century
			grad_year = int(re.search(r"20\d\d", text).group(0))
		except AttributeError:
			raise ClassParseError("Could not parse graduation year")
		# parse campus name in text
		campus = self.get_campus(text)
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
