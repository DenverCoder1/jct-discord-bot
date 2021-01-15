import discord
import utils.utils as utils
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj
import config


class Greeter:
	def __init__(self, intro_channel: discord.TextChannel) -> None:
		self.intro_channel = intro_channel
		self.command_desc = """
		```{config.prefix}join first name, last name, campus, year```

		Where:
		> **first-name** is your first name,
		> **last-name** is your last name,
		> **campus** is *Lev* or *Tal* (case insensitive),
		> **year** is one of 1, 2, 3, or 4

		"""

	async def give_initial_role(self, member: discord.Member):
		label = "BOT_ROLE_ID" if member.bot else "UNASSIGNED_ROLE_ID"
		role = member.guild.get_role(utils.get_id(label))
		await member.add_roles(role)
		print(f"Gave {role.name} to {member.name}")

	async def server_greet(self, member: discord.Member):
		# Sets the channel to the welcome channel and sends a message to it
		channel = get_discord_obj(member.guild.channels, "WELCOME_CHANNEL_ID")
		await channel.send(f"{member.name} joined the server!")
		await channel.send(
			f"""Welcome to the JCT CompSci ESP server, {member.mention}!

			Please type the following command so we know who you are:

			{self.command_desc}

			If you have any trouble feel free to contact an admin using @Admin.
			"""
		)

	async def private_greet(self, member: discord.Member):
		"""privately messages the user who joined"""
		if member.dm_channel == None:
			await member.create_dm()

		channel = get_discord_obj(member.guild.channels, "WELCOME_CHANNEL_ID")

		await member.dm_channel.send(
			f"""Welcome to the JCT CompSci ESP server, {member.mention}!

			If you haven't already done so, please type head over to the {channel.mention} channel in the JCT CompSci ESP server and type the following command so we know who you are:

			{self.command_desc}

			If you have any trouble feel free to contact an admin using @Admin in the {channel.mention} channel.
			"""
		)