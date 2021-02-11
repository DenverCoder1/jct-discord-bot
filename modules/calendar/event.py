from datetime import datetime
from typing import Dict
from utils.utils import parse_date


class Event:
	def __init__(self, details: Dict[str, str], tz: str = None):
		self.details = details
		self.tz = tz or self.details["start"].get("timeZone", None)

	def id(self) -> str:
		return self.details.get("id")

	def html_link(self) -> str:
		return self.details.get("htmlLink")

	def title(self) -> str:
		return self.details.get("summary")

	def all_day(self) -> bool:
		return "date" in self.details["start"]

	def start(self) -> datetime:
		return self.__get_endpoint("start")

	def end(self) -> datetime:
		return self.__get_endpoint("end")

	def timezone(self) -> str:
		return self.tz

	def __get_endpoint(self, endpoint: str) -> datetime:
		return parse_date(
			self.details[endpoint].get("dateTime", self.details[endpoint].get("date")),
			tz=self.timezone(),
		)
