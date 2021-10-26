import asyncio
import os
import asyncpg
import discord
import database.preloaded
from discord_slash import SlashCommand
import config
from discord.ext import commands
from utils.scheduler import Scheduler


async def main():
	# Connect to the database
	config.conn = await asyncpg.connect(os.getenv("DATABASE_URL", ""), ssl="require")
	# Preload necessary data from the database
	await database.preloaded.load()

	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	activity = discord.Game("with students' patience")

	# empty space effectively disables prefix since discord strips trailing spaces
	bot = commands.Bot(" ", intents=intents, activity=activity)

	setattr(bot, "slash", SlashCommand(bot, override_type=True, sync_commands=True))

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
