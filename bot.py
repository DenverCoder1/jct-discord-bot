import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":

	load_dotenv()

	# Discord setup
	TOKEN = os.getenv("DISCORD_TOKEN")
	DISCORD_GUILD = int(os.getenv("DISCORD_GUILD"))

	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	client = commands.Bot("~", intents=intents)  # bot command prefix

	# Get the base file names of all the files in the modules folder
	folders = filter(
		lambda folder: os.path.exists("modules/" + folder + "/cog.py"),
		os.listdir("modules"),
	)

	for folder in folders:
		client.load_extension("modules." + folder + ".cog")

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
