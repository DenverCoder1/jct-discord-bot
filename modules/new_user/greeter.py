import nextcord
import config
from nextcord.ext import commands
from utils import utils


class Greeter:
	"""Greets new users and instructs them on how to use the join command."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def __intro_channel(self):
		return config.guild().get_channel(utils.get_id("INTRO_CHANNEL"))

	async def give_initial_role(self, member: nextcord.Member):
		label = "BOT_ROLE" if member.bot else "UNASSIGNED_ROLE"
		role = member.guild.get_role(utils.get_id(label))
		assert role is not None
		await member.add_roles(role)

	async def server_greet(self, member: nextcord.Member):
		channel = self.__intro_channel()
		assert isinstance(channel, nextcord.TextChannel)
		await utils.delayed_send(channel, 4, f"Hey {member.mention}!")
		await utils.delayed_send(channel, 8, "Welcome to the server!")
		await utils.delayed_send(
			channel, 8, "Please type `/join` and enter the details it asks you for"
		)
		await utils.delayed_send(
			channel, 8, "If you have any trouble tag @Admin and tell them your problem"
		)
		await utils.delayed_send(
			channel, 6, "But just so you dont have to, here's a GIF!"
		)
		await utils.delayed_send(channel, 5, "https://i.imgur.com/5So77B6.gif")

	async def private_greet(self, member: nextcord.Member):
		"""privately messages the user who joined"""
		channel = self.__intro_channel()
		assert isinstance(channel, nextcord.TextChannel)
		await (member.dm_channel or await member.create_dm()).send(
			utils.remove_tabs(
				f"""
				Hey, {member.mention}! Welcome!

				Please type head over to the {channel.mention} channel and follow instructions there.
				"""
			)
		)
