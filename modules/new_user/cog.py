from discord.utils import get
from discord.ext import commands
from modules.new_user.new_user import (
	is_unassigned,
	add_role,
	switch_unassigned,
	change_nick,
	get_id,
)


class new_user(commands.Cog):
	def __init__(self, bot, attempts=None):
		self.bot = bot
		self.attempts = attempts if attempts is not None else {}

	@commands.command(name="join")
	async def join(self, ctx, first_name: str, last_name: str, machon: str, year: str):
		"""Join command to get new users information and place them in the right roles"""
		# user who wrote the command
		member = ctx.author

		if not is_unassigned(member):
			return

		await change_nick(member, first_name, last_name)
		await add_role(ctx, machon, year)
		await switch_unassigned(member)
		del self.attempts[member.name]

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""catch missing required argument error"""
		member = ctx.message.author

		if isinstance(error, commands.MissingRequiredArgument):
			if not is_unassigned(member):
				return

			# check is this user needs extra help
			if member.name not in self.attempts:
				self.attempts[member.name] = 0

			elif self.attempts[member.name] >= 2:
				admin = get(ctx.guild.roles, id=get_id("ADMIN_ROLE_ID"))
				await ctx.send(
					f"{admin.mention} Help! Someone doesn't know how to read!"
				)

			else:
				self.attempts[member.name] += 1

			await ctx.send(
				"""
Please check the syntax of the command:

++join **first-name**, **last-name**, **campus**, **year**

  - **campus** is Lev or Tal (case insensitive),
  - **year** is 1, 2, 3, or 4
"""
			)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		"""Welcome members who join."""
		print(f"{member.name} joined the guild.")

		# Sets the channel to the welcome channel and sends a message to it
		channel = get(member.guild.channels, id=get_id("WELCOME_CHANNEL_ID"))
		await channel.send(
			"""
Welcome to the server!
Please type the following command so we know who you are:

++join **first-name**, **last-name**, **campus**, **year**

Where:
  - **first-name** is your first name,
  - **last-name** is your last name,
  - **campus** is Lev or Tal (case insensitive),
  - **year** is 1, 2, 3, or 4

If you have any trouble feel free to ask an admin for assistance by typing @Admin
"""
		)


# setup functions for bot
def setup(bot):
	bot.add_cog(new_user(bot))