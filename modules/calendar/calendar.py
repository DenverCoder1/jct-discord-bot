from typing import Dict


class Calendar:
	def __init__(self, details: Dict[str, str] = {}, **kwargs):
		"""Create a calendar from a JSON object or kwargs (id and name)"""
		self.calendar_id = kwargs.get("id", details.get("id"))
		self.calendar_name = kwargs.get("name", details.get("summary"))

	def id(self):
		return self.calendar_id

	def name(self):
		return self.calendar_name
