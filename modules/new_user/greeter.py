import discord
import config
from discord.ext import commands
from utils import utils


class Greeter:
	"""Greets new users and instructs them on how to use the join command."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def __intro_channel(self):
		return config.guild().get_channel(utils.get_id("INTRO_CHANNEL"))

	async def give_initial_role(self, member: discord.Member):
		label = "BOT_ROLE" if member.bot else "UNASSIGNED_ROLE"
		role = member.guild.get_role(utils.get_id(label))
		assert role is not None
		await member.add_roles(role)

	async def server_greet(self, member: discord.Member):
		channel = self.__intro_channel()
		await utils.delayed_send(channel, 2, f"Hey {member.mention}!")
		await utils.delayed_send(channel, 4, "Welcome to the server!")
		await utils.delayed_send(
			channel, 4, "Please type `/join` and enter the details it asks you for"
		)
		await utils.delayed_send(
			channel, 3, "If you have any trouble tag @Admin can help you"
		)
		await utils.delayed_send(channel, 2, "But just so you dont, here's a GIF")
		await channel.send("https://i.imgur.com/5So77B6.gif")

	async def private_greet(self, member: discord.Member):
		"""privately messages the user who joined"""
		await (member.dm_channel or await member.create_dm()).send(
			utils.remove_tabs(
				f"""
				Hey, {member.mention}! Welcome!

				Please type head over to the {self.__intro_channel().mention} channel and follow instructions there.
				"""
			)
		)
