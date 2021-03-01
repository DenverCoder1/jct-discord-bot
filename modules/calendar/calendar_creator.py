from typing import Iterable
from utils.sql_fetcher import SqlFetcher
import psycopg2.extensions as sql
from .calendar_service import CalendarService
from .campus import Campus


class CalendarCreator:
	def __init__(
		self, service: CalendarService, conn: sql.connection, sql_fetcher: SqlFetcher
	):
		self.__conn = conn
		self.__sql_fetcher = sql_fetcher
		self.__service = service

	async def create_class_calendars(self, year: int):
		"""Create a calendar for each campus and add it to the database"""
		for campus in await self.__get_campuses():
			# create calendar
			calendar = self.__service.create_calendar(f"JCT CompSci {campus.name} {year}")
			# update class in database
			await self.__add_calendar(calendar.id, campus.id, year)

	async def __get_campuses(self) -> Iterable[Campus]:
		"""Fetch a list of campuses from the database"""
		query = self.__sql_fetcher["get_campuses.sql"]
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				campuses = [Campus(*tup) for tup in cursor.fetchall()]
		return campuses

	async def __add_calendar(self, calendar_id: str, campus_id: int, year: int):
		"""Update the class entry in the database with the calendar id"""
		query = self.__sql_fetcher["add_calendar.sql"]
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query,
					{"calendar_id": calendar_id, "campus_id": campus_id, "year": year},
				)
