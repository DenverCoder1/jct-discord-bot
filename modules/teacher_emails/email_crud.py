from typing import List
from modules.teacher_emails.professor import Professor


class EmailCrud:
	def __init__(self, conn) -> None:
		self.conn = conn

	def search(self, query: str) -> List[Professor]:
		"""returns a list of professors who best match the query"""