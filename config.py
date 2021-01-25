from dotenv.main import load_dotenv
import os
import psycopg2


prefix = "++"

load_dotenv()

# Discord setup
token = os.getenv("DISCORD_TOKEN")

# Connect to database
conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
