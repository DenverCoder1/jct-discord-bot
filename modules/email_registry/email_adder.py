from discord.abc import Messageable
from ..error.friendly_error import FriendlyError
from database import sql_fetcher
from database.person import Person
from psycopg2.errors import UniqueViolation, CheckViolation
import config


def add_email(person: Person, email: str, messageable: Messageable) -> Person:
	"""Add an email address to the database.

	Args:
		person (Person): The person who owns the email address.
		email (str): The email address to add
		messageable (Messageable): The object which errors will be sent to.

	Returns:
		Person: The person object with the email address added.
	"""
	return __add_remove_email("add_email.sql", person, email, messageable)


def remove_email(person: Person, email: str, messageable: Messageable) -> Person:
	"""Remove an email address from the database.

	Args:
		person (Person): The person who the email address belongs to.
		email (str): The email address to be removed from the specified person.
		messageable (Messageable): The object where errors will be sent to.

	Returns:
		Person: The new person object without the email address that was removed.
	"""
	return __add_remove_email("remove_email.sql", person, email, messageable)


def __add_remove_email(
	sql_file: str, person: Person, email: str, messageable: Messageable
) -> Person:
	email = email.strip()
	query = sql_fetcher.fetch("modules", "email_registry", "queries", sql_file)
	with config.conn as conn:
		with conn.cursor() as cursor:
			try:
				cursor.execute(query, {"person_id": person.id, "email": email})
			except UniqueViolation as e:
				raise FriendlyError(
					f"Ignoring request to add {email} to {person.name}; it"
					" is already in the system.",
					messageable=messageable,
					inner=e,
				)
			except CheckViolation as e:
				raise FriendlyError(
					f'"{email}" is not a valid email address.',
					messageable=messageable,
					inner=e,
				)
	return Person.get_person(person.id)