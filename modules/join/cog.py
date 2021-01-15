import utils.utils as utils
from modules.join.assigner import Assigner
from modules.error.friendly_error import FriendlyError
from modules.join.join_parser import JoinParseError, JoinParser
from discord.ext import commands


class NewUserCog(commands.Cog, name="New User"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.assigner = Assigner(bot.get_guild(utils.get_id("JCT_GUILD_ID")))
		self.attempts = {}

	@commands.command(name="join")
	async def join(self, ctx: commands.Context):
		"""
		Join command to get new users information and place them in the right roles

		Usage:
		```
		++join first name, last name, campus, year
		```
		Arguments:

			> **first name**: Your first name
			> **last name**: Your last name
			> **campus**: Lev or Tal
			> **year**: an integer from 1 to 4 (inclusive)

		"""
		try:
			parser = JoinParser(ctx.message.content)
			await self.assigner.assign(
				ctx.author, parser.name(), parser.campus(), parser.year()
			)
		except JoinParseError as err:
			if ctx.author not in self.attempts:
				self.attempts[ctx.author] = 0
			err_msg = str(err)
			if self.attempts[ctx.author] > 1:
				err_msg += (
					f"\n\n{utils.get_discord_obj(ctx.guild.roles, 'ADMIN_ROLE_ID').mention}"
					f" Help! {ctx.author.mention} doesn't seem to be able to read"
					" instructions."
				)
			self.attempts[ctx.author] += 1
			raise FriendlyError(err_msg, ctx.channel, ctx.author)


# setup functions for bot
def setup(bot: commands.Bot):
	bot.add_cog(NewUserCog(bot))