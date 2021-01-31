from modules.error.quiet_warning import QuietWarning
from typing import Iterable, Set
from modules.email_registry.person import Person
from modules.email_registry.sql_path import sql_path
import psycopg2.extensions as sql
from psycopg2.errors import UniqueViolation
import re


class EmailAdder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn

	def add_emails(self, person: Person, emails: Iterable[str]) -> None:
		self.__add_remove_emails("add_email.sql", person, emails)

	def remove_emails(self, person: Person, emails: Iterable[str]) -> None:
		self.__add_remove_emails("remove_email.sql", person, emails)

	def __add_remove_emails(
		self, sql_file: str, person: Person, emails: Iterable[str]
	) -> None:
		query = open(sql_path(sql_file), "r").read()
		with self.conn as conn:
			with conn.cursor() as cursor:
				for email in emails:
					try:
						cursor.execute(query, {"person_id": person.id, "email": email})
					except UniqueViolation:
						raise QuietWarning(
							f"Ignoring request to add {email} to {person.name}; it"
							" already exists."
						)

	def filter_emails(self, strings: Iterable[str]) -> Set[str]:
		"""Given a list of strings returns only those which are email addresses"""
		strings = {s.replace(",", " ").strip() for s in strings}
		return {s for s in strings if self.__is_email(s)}

	def __is_email(self, email: str) -> bool:
		return bool(re.search(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email))