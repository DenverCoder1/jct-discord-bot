class Person:
	def __init__(self, id: id, name: str, emails: str, categories: str) -> None:
		self.id = id
		self.name = name
		self.emails = self.__no_duplicates(emails)
		self.categories = self.__no_duplicates(categories)

	def linked_emails(self) -> str:
		return ", ".join([f"__{email}__" for email in self.emails.split(", ")])

	def __no_duplicates(
		self, list_as_str: str, sep_in: str = ",", sep_out: str = ", "
	) -> str:
		return (
			sep_out.join({elem.strip() for elem in list_as_str.split(sep_in)})
			if list_as_str
			else ""
		)
