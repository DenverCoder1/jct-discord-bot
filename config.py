from dotenv.main import load_dotenv
import os
import psycopg2
import discord
from utils.sql_fetcher import SqlFetcher


prefix = "++"

load_dotenv()

# Discord setup
token = os.getenv("DISCORD_TOKEN")

guild_id = int(os.getenv("DISCORD_GUILD"))
_guild: discord.Guild = None  # To be loaded on ready
guild = lambda: _guild

# Connect to database
conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
sql_fetcher = SqlFetcher()

# Google client configuration
google_config = {
	"type": "service_account",
	"project_id": os.getenv("GOOGLE_PROJECT_ID"),
	"private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
	"private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
	"client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
	"client_id": os.getenv("GOOGLE_CLIENT_ID"),
	"auth_uri": "https://accounts.google.com/o/oauth2/auth",
	"token_uri": "https://oauth2.googleapis.com/token",
	"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
	"client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
}