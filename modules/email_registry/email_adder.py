import nextcord
from asyncpg.exceptions import CheckViolationError, UniqueViolationError

from database import sql
from database.person import Person

from ..error.friendly_error import FriendlyError


async def add_email(person: Person, email: str, sender: nextcord.Interaction) -> Person:
    """Add an email address to the database.

    Args:
            person: The person who owns the email address.
            email: The email address to add
            sender: The object which errors will be sent to.

    Returns:
            Person: The person object with the email address added.
    """
    try:
        await sql.insert(
            "emails",
            on_conflict="(person, email) DO NOTHING",
            person=person.id,
            email=email,
        )
        return await Person.get_person(person.id)
    except UniqueViolationError as e:
        raise FriendlyError(
            f"Ignoring request to add {email} to {person.name}; it is already in the" " system.",
            sender=sender,
            inner=e,
        )
    except CheckViolationError as e:
        raise FriendlyError(
            f'"{email}" is not a valid email address.',
            sender=sender,
            inner=e,
        )


async def remove_email(person: Person, email: str) -> Person:
    """Remove an email address from the database.

    Args:
            person (Person): The person who the email address belongs to.
            email (str): The email address to be removed from the specified person.

    Returns:
            Person: The new person object without the email address that was removed.
    """
    await sql.delete("emails", person=person.id, email=email.strip())
    return await Person.get_person(person.id)
