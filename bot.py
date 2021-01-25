import os
import discord
import config
from discord.ext import commands


def main():
	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	client = commands.Bot(config.prefix, intents=intents)  # bot command prefix

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			client.load_extension(f"modules.{folder}.cog")

	@client.event
	async def on_ready():
		"""When discord is connected"""
		print(f"{client.user.name} has connected to Discord!")
		await client.change_presence(activity=discord.Game("with students' patience"))

	# Run Discord bot
	client.run(config.token)


if __name__ == "__main__":
	main()
