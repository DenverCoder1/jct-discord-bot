import os
from typing import Optional

import asyncpg
import nextcord
from dotenv.main import load_dotenv

load_dotenv()

# Discord setup
token = os.getenv("DISCORD_TOKEN", "")

guild_id = int(os.getenv("DISCORD_GUILD", ""))
_guild: Optional[nextcord.Guild] = None  # To be loaded on ready


def guild() -> nextcord.Guild:
    assert _guild is not None
    return _guild


_conn: Optional[asyncpg.Connection] = None  # The global connection to the database


async def get_connection() -> asyncpg.Connection:
    """Get a connection to the database.

    If a connection has not yet been established or the current connection is closed, a new connection will be established.

    Returns:
        asyncpg.Connection: The connection to the database.
    """
    global _conn
    if _conn is None or _conn.is_closed():
        _conn = await asyncpg.connect(os.getenv("DATABASE_URL"))  # type: ignore
    assert isinstance(
        _conn, asyncpg.Connection
    ), "A connection to the database could not be established."
    return _conn


# Google client configuration
google_config = {
    "type": "service_account",
    "project_id": os.getenv("GOOGLE_PROJECT_ID", ""),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID", ""),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL", ""),
    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
}

# Google Drive folder IDs
drive_folder_id = os.getenv("DRIVE_FOLDER_ID", "")
drive_guidelines_url = os.getenv("DRIVE_GUIDLELINES_URL", "")
