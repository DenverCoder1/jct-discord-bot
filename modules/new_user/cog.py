from modules.error.friendly_error import FriendlyError
from modules.new_user.join_parser import JoinParseError, JoinParser
import discord
from discord.ext import commands
import modules.new_user.utils as utils


class NewUserCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.attempts = {}

	@commands.command(name="join")
	async def join(self, ctx: commands.Context):
		"""Join command to get new users information and place them in the right roles"""
		try:
			parser = JoinParser(ctx.message.content)
			await utils.assign(ctx.author, parser.name, parser.campus, parser.year)
		except JoinParseError as err:
			if ctx.author not in self.attempts:
				self.attempts[ctx.author] = 0
			err_msg = str(err)
			if self.attempts[ctx.author] > 1:
				err_msg += (
					f"\n{utils.get_discord_obj(ctx.guild.roles, 'ADMIN_ROLE_ID').mention}"
					f" Help! {ctx.author.mention} doesn't seem to be able to read"
					" instructions."
				)
			self.attempts[ctx.author] += 1
			raise FriendlyError(err_msg, ctx.channel, ctx.author)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		"""Welcome members who join."""
		print(f"{member.name} joined the server.")

		await utils.give_initial_role(member)

		if not member.bot:
			await utils.server_greet(member)
			await utils.private_greet(member)


# setup functions for bot
def setup(bot):
	bot.add_cog(NewUserCog(bot))