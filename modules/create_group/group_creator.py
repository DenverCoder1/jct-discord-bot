from typing import Iterable

from modules.calendar.calendar_creator import CalendarCreator
from modules.calendar.calendar_service import CalendarService

from .new_group import NewGroup


async def create_groups(year: int) -> Iterable[NewGroup]:
    calendar_creator = CalendarCreator(CalendarService("Asia/Jerusalem"))
    calendars = await calendar_creator.create_group_calendars(year)
    groups = [NewGroup(campus, year, calendar) for campus, calendar in calendars.items()]
    for new_group in groups:
        await new_group.add_to_system()
    return groups
