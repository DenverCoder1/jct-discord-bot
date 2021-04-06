import discord
from discord.ext import commands
from utils import utils


class Greeter:
	"""Greets new users and instructs them on how to use the join command."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.command_desc = utils.remove_tabs(
			f"""
			```/join first_name, last_name, campus, year```

			Where:
			> **first_name** is your first name,
			> **last_name** is your last name,
			> **campus** is *Lev* or *Tal*,
			> **year** is one of Year 1, Year 2, Year 3, or Year 4

			"""
		)

	def __intro_channel(self):
		guild = self.bot.get_guild(utils.get_id("JCT_GUILD"))
		return guild.get_channel(utils.get_id("INTRO_CHANNEL"))

	async def give_initial_role(self, member: discord.Member):
		label = "BOT_ROLE" if member.bot else "UNASSIGNED_ROLE"
		role = member.guild.get_role(utils.get_id(label))
		await member.add_roles(role)
		print(f"Gave {role.name} to {member.name}")

	async def server_greet(self, member: discord.Member):
		await self.__intro_channel().send(
			utils.remove_tabs(
				f"""Welcome to the JCT CompSci ESP server, {member.mention}!

				Please type the following command so we know who you are:

				{self.command_desc}

				If you have any trouble feel free to contact an admin using @Admin.
				"""
			)
		)

	async def private_greet(self, member: discord.Member):
		"""privately messages the user who joined"""
		if member.dm_channel == None:
			await member.create_dm()

		await member.dm_channel.send(
			utils.remove_tabs(
				f"""
				Welcome to the JCT CompSci ESP server, {member.mention}!

				If you haven't already done so, please type head over to the {self.__intro_channel().mention} channel in the JCT CompSci ESP server and type the following command so we know who you are:

				{self.command_desc}

				If you have any trouble feel free to contact an admin using @Admin in the {self.__intro_channel().mention} channel.
				"""
			)
		)
