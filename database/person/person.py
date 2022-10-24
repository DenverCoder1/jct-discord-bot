from typing import Iterable, Sequence, Set, Tuple

import config
from database import sql, sql_fetcher


class Person:
    def __init__(self, id: int, name: str, emails: str, categories: str) -> None:
        self.__id = id
        self.__name = name
        self.__emails = self.__no_duplicates(emails)
        self.__categories = self.__no_duplicates(categories)

    @property
    def id(self) -> int:
        """The ID of this person as stored in the database."""
        return self.__id

    @property
    def name(self) -> str:
        """The name of this person."""
        return self.__name

    @property
    def emails(self) -> Iterable[str]:
        """An iterable containing the email addresses registered to this person."""
        return self.__emails.split(", ")

    @property
    def categories(self) -> str:
        """A comma separated string of categories this person is associated with."""
        return self.__categories

    @property
    def linked_emails(self) -> str:
        """A comma separated string of underlined email addresses of this person."""
        return ", ".join([f"__{email}__" for email in self.__emails.split(", ") if email])

    def __no_duplicates(self, list_as_str: str, sep_in: str = ",", sep_out: str = ", ") -> str:
        return (
            sep_out.join({elem.strip() for elem in list_as_str.split(sep_in)})
            if list_as_str
            else ""
        )

    @classmethod
    async def get_person(cls, person_id: int) -> "Person":
        """Searches the database for a person with a given id and returns a Person object."""
        record = await sql.select.one(
            "people_view", ("id", "name", "emails", "categories"), id=person_id
        )
        assert record is not None
        return cls(*record)

    @classmethod
    async def get_people(cls) -> Set["Person"]:
        """Searches the database for all people and returns a set of Person objects."""
        records = await sql.select.many("people_view", ("name", "emails", "categories"))
        return {cls(*record) for record in records}

    @classmethod
    async def search_by_name(cls, name: str) -> Sequence[Tuple["Person", float]]:
        """Searches the database for all people whose name or surname reasonably match the input and returns a sequence of (person, similarity) pairs sorted by decreasing similarity.

        Args:
            name (str): The name of the person to search for.

        Returns:
            Sequence[Tuple[Person, float]]: A sequence of results where each result is a tuple of the person that matched as well as a similarity score between 0 and 1.
        """
        query = sql_fetcher.fetch("database", "person", "queries", "search_people.sql")
        return [(cls(*record[:-1]), record[-1]) for record in await config.conn.fetch(query, name)]

    @classmethod
    async def search_by_channel(cls, channel_id: int) -> Iterable["Person"]:
        """
        Searches the database for all people whose channel matches the input and returns an iterable of these.
        """
        return await cls.__search_people("person_category_categories_view", channel=channel_id)

    @classmethod
    async def search_by_email(cls, email: str) -> Iterable["Person"]:
        """
        Searches the database for all people whose email matches the input and returns an iterable of these.
        """
        return await cls.__search_people("emails", email=email)

    def __eq__(self, other):
        """Compares them by ID"""
        if isinstance(other, self.__class__):
            return self.__id == other.__id
        return False

    def __hash__(self):
        return hash(self.__id)

    @classmethod
    async def __search_people(cls, table: str, **conditions) -> Iterable["Person"]:
        """Searches the database using a given a table and some kwarg conditions and returns a list of people found.

        Args:
            table (str): The name of the table to search in.
            **conditions: The column names and values that the found records should have.

        Returns:
            Iterable[Person]: An iterable of the people found.
        """
        records = await sql.select.many(table, ("person",), **conditions)
        return {await Person.get_person(record["person"]) for record in records}
