from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from utils.utils import format_date, parse_date


class Event:
	def __init__(self, details: Dict[str, Any], tz: Optional[str] = None):
		self.__details = details
		self.__tz = tz or self.__details["start"].get("timeZone", None)

	@property
	def event_id(self) -> str:
		"""Returns the event id"""
		return self.__details.get("id")

	@property
	def link(self) -> str:
		"""Returns the link to the event in Google Calendar"""
		return self.__details.get("htmlLink")

	@property
	def title(self) -> str:
		"""Returns the title of the event"""
		return self.__details.get("summary")

	@property
	def all_day(self) -> bool:
		"""Returns whether or not the event is an all day event"""
		return "date" in self.__details["start"]

	@property
	def start(self) -> datetime:
		"""Returns the start date as a datetime object"""
		return self.__get_endpoint("start")

	@property
	def end(self) -> datetime:
		"""Returns the end date as a datetime object"""
		return self.__get_endpoint("end")

	@property
	def start_str(self) -> str:
		"""Returns a formatted string of the start date"""
		return format_date(self.start, all_day=self.all_day) or "Today"

	def end_str(self, base: datetime=datetime.now()) -> str:
		"""Returns a formatted string of the end date"""
		end_date = self.end
		# use previous day if end of multi-day, all-day event
		if self.all_day and not self.__one_day():
			end_date -= timedelta(days=1)
		return format_date(end_date, all_day=self.all_day, base=base)

	@property
	def date_range_str(self) -> str:
		"""Returns a formatted string of the start to end date range"""
		start_str = self.start_str
		end_str = self.end_str(base=self.start)
		# all day event
		if self.__one_day():
			return f"{start_str} - All day"
		# include end time if it is not the same as the start time
		return f"{start_str} - {end_str}" if end_str else start_str

	@property
	def timezone(self) -> str:
		"""Returns the timezone passed to the constructor \
			or the event's timezone if not specified. \
			If neither are present, returns None."""
		return self.__tz

	@property
	def location(self) -> str:
		"""Returns the location of the event"""
		return self.__details.get('location')

	@property
	def description(self) -> str:
		"""Returns the description of the event"""
		return self.__details.get('description')

	def __get_endpoint(self, endpoint: str) -> datetime:
		"""Returns a datetime given 'start' or 'end' as the endpoint"""
		dt = parse_date(
			self.__details[endpoint].get("dateTime", self.__details[endpoint].get("date")),
			from_tz=self.timezone,
			to_tz=self.timezone
		)
		if dt:
			return dt
		raise ValueError("Unable to parse date.")

	def __one_day(self) -> bool:
		"""Returns whether or not the event is a one day event"""
		return self.all_day and self.end - self.start <= timedelta(days=1)
