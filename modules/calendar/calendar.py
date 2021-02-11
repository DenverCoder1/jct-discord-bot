from typing import Dict


class Calendar:
	def __init__(self, details: Dict[str, str]):
		self.details = details

	def id(self):
		return self.details.get("id")

	def name(self):
		return self.details.get("summary")
