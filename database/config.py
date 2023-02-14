import os
from typing import Optional

import asyncpg
from dotenv.main import load_dotenv

load_dotenv()

# The global connection to the database
_conn: Optional[asyncpg.Connection] = None


async def get_connection() -> asyncpg.Connection:
    """Get a connection to the database.

    If a connection has not yet been established or the current connection is closed, a new connection will be established.

    Returns:
        asyncpg.Connection: The connection to the database.
    """
    global _conn
    if _conn is None or _conn.is_closed():
        _conn = await asyncpg.connect(os.getenv("DATABASE_URL", ""), ssl="require")  # type: ignore
    assert isinstance(
        _conn, asyncpg.Connection
    ), "A connection to the database could not be established."
    return _conn
