import config
import discord
from discord.ext import commands
import modules.new_user.new_user as new_user


class NewUserCog(commands.Cog):
	def __init__(self, bot, attempts=None):
		self.bot = bot
		self.attempts = attempts if attempts is not None else {}

	@commands.command(name="join")
	async def join(self, ctx, first_name: str, last_name: str, machon: str, year: str):
		"""Join command to get new users information and place them in the right roles"""
		# user who wrote the command
		member = ctx.author

		if not new_user.is_unassigned(member):
			return

		await new_user.change_nick(member, first_name, last_name)
		await new_user.add_role(ctx, machon, year)
		await new_user.switch_unassigned(member)
		del self.attempts[member.name]

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""catch missing required argument error"""
		member = ctx.message.author

		if isinstance(error, commands.MissingRequiredArgument):
			if not new_user.is_unassigned(member):
				return

			# check is this user needs extra help
			if member.name not in self.attempts:
				self.attempts[member.name] = 0

			elif self.attempts[member.name] >= 2:
				admin = discord.utils.get(
					ctx.guild.roles, id=new_user.get_id("ADMIN_ROLE_ID")
				)
				await ctx.send(
					f"{admin.mention} Help! Someone doesn't know how to read!"
				)

			else:
				self.attempts[member.name] += 1

			await ctx.send(
				f"""
Please check the syntax of the command:

{config.prefix}join **first-name**, **last-name**, **campus**, **year**

  - **campus** is Lev or Tal (case insensitive),
  - **year** is 1, 2, 3, or 4
"""
			)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		"""Welcome members who join."""
		print(f"{member.name} joined the guild.")

		# If new member is a bot, give them the bot role and don't welcome them
		if member.bot:
			await member.add_roles(
				discord.utils.get(member.guild.roles, id=new_user.get_id("BOT_ROLE_ID"))
			)
			return

		# TODO: Give user unassigned role

		# Sets the channel to the welcome channel and sends a message to it
		channel = discord.utils.get(
			member.guild.channels, id=new_user.get_id("WELCOME_CHANNEL_ID")
		)
		await channel.send(
			f"""
Welcome to the server!
Please type the following command so we know who you are:

{config.prefix}join **first-name**, **last-name**, **campus**, **year**

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
	bot.add_cog(NewUserCog(bot))