class Person:
	def __init__(self, id: id, name: str, emails: str, categories: str) -> None:
		self.id = id
		self.name = name
		self.emails = (
			" ".join(set(emails.replace(",", " ").split()))
			if emails is not None
			else ""
		)
		self.categories = categories

	def linked_emails(self) -> str:
		return ", ".join([f"__{email}__" for email in self.emails.split()])
