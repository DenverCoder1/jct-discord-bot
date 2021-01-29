class Professor:
	def __init__(self, id: id, name: str, emails: str, subjects: str) -> None:
		self.id = id
		self.name = name
		self.emails = " ".join(set(emails.split())) if emails is not None else ""
		self.subjects = subjects

	def linked_emails(self) -> str:
		return ", ".join([f"__{email}__" for email in self.emails.split()])
