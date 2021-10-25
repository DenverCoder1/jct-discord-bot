from typing import (
	Any,
	Coroutine,
	Iterable,
	List,
	Optional,
	Protocol,
	TypeVar,
)
import asyncpg
import config
from . import util


async def many(
	table: str, columns: Iterable[str] = ("*",), **conditions
) -> List[asyncpg.Record]:
	"""Select all rows in a table matching the kwargs `conditions`.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		table (str): The name of the table to select from.
		columns (Iterable[str], optional): The names of columns to select. Defaults to all columns.
		**conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

	Returns:
		List[asyncpg.Record]: A list of the records in the table.
	"""
	return await __select(table, columns, config.conn.fetch, **conditions)


async def one(
	table: str, columns: Iterable[str] = ("*",), **conditions
) -> Optional[asyncpg.Record]:
	"""Select a single row from a table matching the kwargs `conditions`.

	For security reasons it is important that the only user input passed into this function is via the values of `**conditions`.

	Args:
		table (str): The name of the table to select from.
		columns (Iterable[str], optional): The names of the columns to select. Defaults to all columns.
		**conditions: Keyword arguments specifying constraints on the select statement. For a kwarg A=B, the select statement will only match rows where the column named A has the value B.

	Returns:
		Optional[asyncpg.Record]: The selected row if one was found, or None otherwise.
	"""
	return await __select(table, columns, config.conn.fetchrow, **conditions)


T = TypeVar("T", covariant=True)


class Fetcher(Protocol[T]):
	def __call__(self, query: str, *values: Any) -> Coroutine[Any, Any, T]:
		...


async def __select(
	table: str, columns: Iterable[str], fetcher: Fetcher[T], **conditions
) -> T:
	filtered_columns, values, placeholders = util.prepare_kwargs(conditions)
	query = (
		f"SELECT {', '.join(columns)} FROM"
		f" {table}{util.where(filtered_columns, placeholders)}"
	)
	return await fetcher(query, *values)
