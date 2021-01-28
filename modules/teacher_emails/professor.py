from typing import List


class Professor:
	def __init__(self, name: str, email: str, subjects: str) -> None:
		self.name = name
		self.email = email
		self.subjects = subjects