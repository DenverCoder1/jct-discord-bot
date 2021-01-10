from discord.utils import get
from discord.ext import commands
from modules.new_user.new_user import is_unassigned, add_role, switch_unassigned, change_nick, get_id, check_attempts, format_command

class NewUserCog(commands.Cog):
	def __init__ (self, bot, attempts={}):
		self.bot = bot
		self.attempts = attempts

	@commands.command(name="join")
	async def join(self, ctx):
		"""Join command to get new users information and place them in the right roles"""
		#user who wrote the command
		member = ctx.author

		if not is_unassigned(member):
			return

		try:
			(first_name, last_name, machon, year) = await format_command(ctx, ctx.message.content)

		except TypeError:
			check_attempts(ctx, self.attempts)
			return

		await change_nick(member, first_name, last_name)
		await add_role(ctx, machon, year)
		await switch_unassigned(member)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		"""Welcome members who join."""
		print(f"{member.name} joined the guild.")

		#Give "unassigned" role to new members
		unassigned = get(member.guild.roles, id=get_id("UNASSIGNED_ROLE_ID"))
		await member.add_roles(unassigned)
		print(f"Gave Unassigned to {member.name}")

		#Sets the channel to the welcome channel and sends a message to it
		channel = get(member.guild.channels, id=get_id("WELCOME_CHANNEL_ID"))
		await channel.send(f"Welcome to the server, {member.mention}!\nPlease type the following command so we know who you are:\n\n~join first-name, last-name, campus, year\n\n Where:\n\n\t\t- **first-name** is your first name,\n\t\t- **last-name** is your last name,\n\t\t- **campus**: Lev or Tal (case insensitive),\n\t\t- **year**: one of 1, 2, 3, or 4\n\nIf you have any trouble feel free to contact an admin using @Admin")

		#privately messages the user who joined
		if member.dm_channel == None:
			await member.create_dm()

		await member.dm_channel.send(f"Welcome to the server, {member.mention}!\nPlease type the following command in {channel.mention} so we know who you are:\n\n~join first-name, last-name, campus, year\n\n Where:\n\n\t\t- **first-name** is your first name,\n\t\t- **last-name** is your last name,\n\t\t- **campus**: Lev or Tal (case insensitive),\n\t\t- **year**: one of 1, 2, 3, or 4\n\nIf you have any trouble feel free to contact an admin using @Admin")


#setup functions for bot
def setup(bot):
	bot.add_cog(NewUserCog(bot))