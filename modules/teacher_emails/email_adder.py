from typing import Iterable, Set
from modules.teacher_emails.professor import Professor
from modules.teacher_emails.sql_path import sql_path
import psycopg2.extensions as sql
import re


class EmailAdder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn

	def add_emails(self, prof: Professor, emails: Iterable[str]) -> None:
		cursor = self.conn.cursor()
		query = open(sql_path("add_email.sql"), "r").read()
		for email in emails:
			cursor.execute(query, {"t_id": prof.id, "email": email})
		self.conn.commit()
		cursor.close()

	def filter_emails(self, strings: Iterable[str]) -> Set[str]:
		"""Given a list of strings returns only those which are email addresses"""
		return {s for s in strings if self.__is_email(s)}

	def __is_email(self, email: str) -> bool:
		return bool(re.search(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email))