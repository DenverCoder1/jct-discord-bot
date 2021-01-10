import config
import discord
from discord.ext import commands
import modules.new_user.utils as utils


class NewUserCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.attempts = {}

	@commands.command(name="join")
	async def join(self, ctx):
		"""Join command to get new users information and place them in the right roles"""
		await utils.assign(ctx, self.attempts)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		"""Welcome members who join."""
		print(f"{member.name} joined the guild.")

		# If new member is a bot, give them the bot role and don't welcome them
		if member.bot:
			await member.add_roles(
				discord.utils.get(member.guild.roles, id=utils.get_id("BOT_ROLE_ID"))
			)
			return

		# Give "unassigned" role to new members
		unassigned = utils.get(
			member.guild.roles, id=utils.get_id("UNASSIGNED_ROLE_ID")
		)
		await member.add_roles(unassigned)
		print(f"Gave Unassigned to {member.name}")

		# Sets the channel to the welcome channel and sends a message to it
		channel = discord.utils.get(
			member.guild.channels, id=utils.get_id("WELCOME_CHANNEL_ID")
		)
		await channel.send(
			f"Welcome to the server, {member.mention}!\n"
			"\n"
			"Please type the following command so we know who you are:\n"
			"\n"
			f"{config.prefix}join **first-name**, **last-name**, **campus**, **year\n"
			"\n"
			"Where:\n"
			"  - **first-name** is your first name,\n"
			"  - **last-name** is your last name,\n"
			"  - **campus** is *Lev* or *Tal* (case insensitive),\n"
			"  - **year** is one of 1, 2, 3, or 4\n"
			"\n"
			"If you have any trouble feel free to contact an admin using @Admin\n"
		)

		# privately messages the user who joined
		if member.dm_channel == None:
			await member.create_dm()

		await member.dm_channel.send(
			f"Welcome to the server, {member.mention}!\n\nPlease type head over to the"
			f" {channel.mention} channel and type the following command so we know who"
			" you are:\n\n~join **first-name**, **last-name**, **campus**,"
			" **year**\n\nWhere:\n  - **first-name** is your first name,\n  -"
			" **last-name** is your last name,\n  - **campus** is *Lev* or *Tal* (case"
			" insensitive),\n  - **year** is one of 1, 2, 3, or 4\n\nIf you have any"
			" trouble feel free to contact an admin using @Admin\n"
		)


# setup functions for bot
def setup(bot):
	bot.add_cog(NewUserCog(bot))