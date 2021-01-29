class Professor:
	def __init__(self, name: str, emails: str, subjects: str) -> None:
		self.name = name
		self.emails = " ".join(set(emails.split()))
		self.subjects = subjects

	def linked_emails(self) -> str:
		return ", ".join([f"__{email}__" for email in self.emails.split()])
