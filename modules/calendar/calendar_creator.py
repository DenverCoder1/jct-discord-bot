from database import sql_fetcher
import psycopg2.extensions as sql
from .calendar_service import CalendarService
from database.campus import Campus


class CalendarCreator:
	def __init__(self, service: CalendarService, conn: sql.connection):
		self.__conn = conn
		self.__service = service

	def create_group_calendars(self, year: int):
		"""Create a calendar for each campus and add it to the database"""
		for campus in Campus.get_campuses():
			# create calendar
			calendar = self.__service.create_calendar(
				f"JCT CompSci {campus.name} {year}"
			)
			# update class in database
			self.__add_calendar(calendar.id, campus.id, year)

	def __add_calendar(self, calendar_id: str, campus_id: int, year: int):
		"""Update the class entry in the database with the calendar id"""
		query = sql_fetcher.fetch("modules", "calendar", "queries", "add_calendar.sql")
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query,
					{"calendar_id": calendar_id, "campus_id": campus_id, "year": year},
				)
