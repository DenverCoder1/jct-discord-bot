import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents

if __name__ == "__main__":

	load_dotenv()

	# Discord setup
	TOKEN = os.getenv("DISCORD_TOKEN")
	DISCORD_GUILD = int(os.getenv("DISCORD_GUILD"))

	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	global PREFIX
	PREFIX = "++"
	client = commands.Bot(PREFIX, intents=intents)  # bot command prefix

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			client.load_extension("modules." + folder + ".cog")

	# TODO: remove this code by February (or whenever people get used to the new prefix)
	@client.event
	async def on_message(message: discord.Message):
		if message.content.startswith("~"):
			channel = message.channel
			await channel.send(
				"The prefix `~` has been changed to `++`. Please use that instead."
			)
			await channel.send("++" + message.content[1:])

	@client.event
	async def on_ready():
		"""When discord is connected"""
		print(f"{client.user.name} has connected to Discord!")

	@client.event
	async def on_error(event, *args, **kwargs):
		"""When an exception is raised, log it in err.log"""
		with open("err.log", "a") as f:
			if event == "on_message":
				f.write(f"Unhandled message: {args[0]}\n")
			else:
				f.write(f"Event: {event}\nMessage: {args}\n")

	# Run Discord bot
	client.run(TOKEN)
