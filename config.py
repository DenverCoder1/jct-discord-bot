from dotenv.main import load_dotenv
import os


def init():
	global prefix, token, guild_id
	prefix = "++"

	load_dotenv()

	# Discord setup
	token = os.getenv("DISCORD_TOKEN")
	guild_id = int(os.getenv("DISCORD_GUILD"))
