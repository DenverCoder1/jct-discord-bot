from typing import Set
import config


class Person:
	def __init__(self, id: id, name: str, emails: str, categories: str) -> None:
		self.id = id
		self.name = name
		self.emails = self.__no_duplicates(emails)
		self.categories = self.__no_duplicates(categories)

	def linked_emails(self) -> str:
		return ", ".join([f"__{email}__" for email in self.emails.split(", ") if email])

	def __no_duplicates(
		self, list_as_str: str, sep_in: str = ",", sep_out: str = ", "
	) -> str:
		return (
			sep_out.join({elem.strip() for elem in list_as_str.split(sep_in)})
			if list_as_str
			else ""
		)

	@staticmethod
	def get_person(person_id: int) -> "Person":
		"""Searches the database for a person with a given id and returns a Person object."""
		query = config.sql_fetcher.fetch(
			"database", "person", "queries", "get_person.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"person_id": person_id})
				return Person(*cursor.fetchone())

	@staticmethod
	def get_people() -> Set["Person"]:
		"""Searches the database for all people and returns a set of Person objects."""
		query = config.sql_fetcher.fetch(
			"database", "person", "queries", "get_people.sql"
		)
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				people = {Person(*row) for row in cursor.fetchall()}
		return people