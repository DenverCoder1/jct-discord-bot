from typing import Set
import config
from database import sql_fetcher


class Person:
	def __init__(self, id: id, name: str, emails: str, categories: str) -> None:
		self.__id = id
		self.__name = name
		self.__emails = self.__no_duplicates(emails)
		self.__categories = self.__no_duplicates(categories)

	@property
	def person_id(self) -> int:
		"""The ID of this person as stored in the database."""
		return self.__id

	@property
	def name(self) -> str:
		"""The name of this person."""
		return self.__name

	@property
	def emails(self) -> str:
		"""A comma separated string of email addresses of this person."""
		return self.__emails

	@property
	def categories(self) -> str:
		"""A comma separated string of categories this person is associated with."""
		return self.__categories

	@property
	def linked_emails(self) -> str:
		"""A comma separated string of underlined email addresses of this person."""
		return ", ".join(
			[f"__{email}__" for email in self.__emails.split(", ") if email]
		)

	def __no_duplicates(
		self, list_as_str: str, sep_in: str = ",", sep_out: str = ", "
	) -> str:
		return (
			sep_out.join({elem.strip() for elem in list_as_str.split(sep_in)})
			if list_as_str
			else ""
		)

	@classmethod
	def get_person(cls, person_id: int) -> "Person":
		"""Searches the database for a person with a given id and returns a Person object."""
		query = sql_fetcher.fetch("database", "person", "queries", "get_person.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"person_id": person_id})
				return cls(*cursor.fetchone())

	@classmethod
	def get_people(cls) -> Set["Person"]:
		"""Searches the database for all people and returns a set of Person objects."""
		query = sql_fetcher.fetch("database", "person", "queries", "get_people.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				people = {cls(*row) for row in cursor.fetchall()}
		return people

	def __eq__(self, other):
		"""Compares them by ID"""
		if isinstance(other, self.__class__):
			return self.__id == other.__id
		return False

	def __hash__(self):
		return hash(self.__id)
