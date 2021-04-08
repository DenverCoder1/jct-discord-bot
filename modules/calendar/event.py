from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from utils.utils import format_date, parse_date


class Event:
	"""Event object to store data about a Google Calendar event"""

	def __init__(
		self,
		event_id: str,
		link: str,
		title: str,
		location: Optional[str],
		description: Optional[str],
		all_day: bool,
		start: datetime,
		end: datetime,
		timezone: str,
	):
		self.__id = event_id
		self.__link = link
		self.__title = title
		self.__location = location
		self.__description = description
		self.__all_day = all_day
		self.__start = start.replace(tzinfo=None)
		self.__end = end.replace(tzinfo=None)
		self.__timezone = timezone

	@property
	def id(self) -> str:
		"""Returns the event id"""
		return self.__id

	@property
	def link(self) -> str:
		"""Returns the link to the event in Google Calendar"""
		return self.__link

	@property
	def title(self) -> str:
		"""Returns the title of the event"""
		return self.__title

	@property
	def location(self) -> Optional[str]:
		"""Returns the location of the event"""
		return self.__location

	@property
	def description(self) -> Optional[str]:
		"""Returns the description of the event"""
		return self.__description

	@property
	def all_day(self) -> bool:
		"""Returns whether or not the event is an all day event"""
		return self.__all_day

	@property
	def start(self) -> datetime:
		"""Returns the start date as a datetime object"""
		return self.__start

	@property
	def end(self) -> datetime:
		"""Returns the end date as a datetime object"""
		return self.__end

	@property
	def timezone(self) -> str:
		"""Returns the timezone passed to the constructor or the calendar's timezone if not specified."""
		return self.__timezone

	@property
	def __one_day(self) -> bool:
		"""Returns whether or not the event is a one day event"""
		return self.all_day and self.end - self.start <= timedelta(days=1)

	def relative_date_range_str(self, base=datetime.now()) -> str:
		"""Returns a formatted string of the start to end date range"""
		start_str = self.__relative_start_str(base=base)
		end_str = self.__relative_end_str(base=self.start)
		# all day event
		if self.__one_day:
			return f"{start_str} - All day"
		# include end time if it is not the same as the start time
		return f"{start_str} - {end_str}" if end_str else start_str

	def __relative_start_str(self, base=datetime.now()) -> str:
		"""Returns a formatted string of the start date"""
		return format_date(self.start, all_day=self.all_day, base=base) or "Today"

	def __relative_end_str(self, base=datetime.now()) -> str:
		"""Returns a formatted string of the end date"""
		end_date = self.end
		# use previous day if end of multi-day, all-day event
		if self.all_day and not self.__one_day:
			end_date -= timedelta(days=1)
		return format_date(end_date, all_day=self.all_day, base=base)

	@classmethod
	def from_dict(cls, details: Dict[str, Any]) -> "Event":
		"""Create an event from a JSON object as returned by the Calendar API"""
		return cls(
			event_id=details["id"],
			link=details["htmlLink"],
			title=details["summary"],
			all_day=("date" in details["start"]),
			location=details.get("location"),
			description=details.get("description"),
			start=cls.get_endpoint_datetime(details, "start"),
			end=cls.get_endpoint_datetime(details, "end"),
			timezone=details["start"]["timeZone"],
		)

	@staticmethod
	def get_endpoint_datetime(details: Dict[str, Any], endpoint: str) -> datetime:
		"""Returns a datetime given 'start' or 'end' as the endpoint"""
		dt = parse_date(
			details[endpoint].get("dateTime") or details[endpoint]["date"],
			from_tz=details[endpoint]["timeZone"],
			to_tz=details[endpoint]["timeZone"],
		)
		assert dt is not None
		return dt
