from typing import Dict


class Calendar:
	def __init__(self, details: Dict[str, str] = {}, **kwargs):
		"""Create a calendar from a JSON object or kwargs (id and name)"""
		self.id = kwargs.get("id", details.get("id"))
		self.name = kwargs.get("name", details.get("summary"))
