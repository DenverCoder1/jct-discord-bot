import os
import discord
from discord.ext.commands.core import command
import config
from discord.ext import commands


def main():
	config.init()

	# allows privledged intents for monitoring members joining, roles editing, and role assignments (has to be enabled for the bot in Discord dev)
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	client = commands.Bot(config.prefix, intents=intents)  # bot command prefix

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			client.load_extension(f"modules.{folder}.cog")

	# TODO: remove this code by February (or whenever people get used to the new prefix)
	@client.event
	async def on_message(message: discord.Message):
		print(message.content)
		if message.content.startswith(
			tuple(
				f"~{command}"
				for command in os.listdir("modules")
				if os.path.exists(os.path.join("modules", command, "cog.py"))
			)
			+ ("~help",)
		):
			channel = message.channel
			await channel.send(
				f"The prefix `~` has been changed to `{config.prefix}`. Please use that"
				" instead."
			)
		await client.process_commands(message)

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
	client.run(config.token)


if __name__ == "__main__":
	main()