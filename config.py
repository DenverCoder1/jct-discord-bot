from dotenv.main import load_dotenv
import os


prefix = "++"

load_dotenv()

# Discord setup
token = os.getenv("DISCORD_TOKEN")