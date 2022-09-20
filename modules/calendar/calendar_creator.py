from typing import Dict
from modules.calendar.calendar import Calendar
from .calendar_service import CalendarService
from database.campus import Campus


class CalendarCreator:
	def __init__(self, service: CalendarService):
		self.__service = service

	async def create_group_calendars(self, year: int) -> Dict[Campus, Calendar]:
		"""Create a calendar for each campus.

		Args:
			year (int): The year to create the calendars for.

		Returns:
			Dict[int, Calendar]: A dict mapping from campus ID to the newly created calendar objects.
		"""
		return {
			campus: self.__service.create_calendar(f"JCT CompSci {campus.name} {year}")
			for campus in await Campus.get_campuses()
		}
