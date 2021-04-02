from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
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
		query = self.sql_fetcher.fetch(
			"modules", "calendar", "queries", "search_calendar.sql"
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
			"modules", "calendar", "queries", "search_campus.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"text": text})
				row = cursor.fetchall()
		if row is not None and len(row) == 1:
			return row[0][0]
		else:
			raise ClassRoleError(f"Could not find a matching campus name.")

	def get_calendar(self, ctx: SlashContext, class_role: str = None) -> Calendar:
		"""Returns Calendar given a discord member or a string containing the name and id"""
		# parse name and calendar id from selected choice
		if class_role is not None:
			calendar_name, calendar_id = class_role.rsplit(" ", 1)
			return Calendar(name=calendar_name, id=calendar_id)
		# get calendar from user's role
		else:
			try:
				return self.__calendar_from_role(ctx.author)
			except (ClassRoleError, ClassParseError) as error:
				raise FriendlyError(error.args[0], ctx, ctx.author, error)

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
			"modules", "calendar", "queries", "get_class_roles.sql"
		)
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query, {"roles": tuple(role.id for role in member.roles)}
				)
				return cursor.fetchall()

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
