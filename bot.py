import os
import discord
from discord_slash import SlashCommand
import config
from discord.ext import commands
from utils.scheduler import Scheduler


def main():
	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	bot = commands.Bot("/", intents=intents)  # bot command prefix
	setattr(bot, "slash", SlashCommand(bot, override_type=True, sync_commands=True))

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			bot.load_extension(f"modules.{folder}.cog")

	@bot.event
	async def on_ready():
		"""When discord is connected"""
		print(f"{bot.user.name} has connected to Discord!")
		config._guild = bot.get_guild(config.guild_id)
		await bot.change_presence(activity=discord.Game("with students' patience"))
		# Start Scheduler
		Scheduler(bot)

	# Run Discord bot
	bot.run(config.token)


if __name__ == "__main__":
	main()
