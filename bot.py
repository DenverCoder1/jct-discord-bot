import asyncio
import os
import asyncpg
import nextcord
import database.preloaded
import config
from nextcord.ext import commands
from utils.scheduler import Scheduler


async def main():
	# Connect to the database
	config.conn = await asyncpg.connect(os.getenv("DATABASE_URL", ""), ssl="require")
	# Preload necessary data from the database
	await database.preloaded.load()

	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = nextcord.Intents.default()
	intents.guilds = True
	intents.members = True

	activity = nextcord.Game("with students' patience")

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = commands.Bot(" ", intents=intents, activity=activity)

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			bot.load_extension(f"modules.{folder}.cog")

	@bot.event
	async def on_ready():
		"""When discord is connected"""
		# skip if this function has already run
		if config._guild is not None:
			return
		print(f"{bot.user.name} has connected to Discord!")
		config._guild = bot.get_guild(config.guild_id)
		# Start Scheduler
		Scheduler(bot)

	# Run Discord bot
	await bot.start(config.token)


if __name__ == "__main__":
	asyncio.run(main())
