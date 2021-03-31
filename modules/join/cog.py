import os
from utils import utils
from modules.join.assigner import Assigner
from modules.error.friendly_error import FriendlyError
from modules.join.join_parser import JoinParseError, JoinParser
from discord.ext import commands
from utils.sql_fetcher import SqlFetcher
import config
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice


class JoinCog(commands.Cog, name="Join"):
	"""Join command to get new users information and place them in the right roles"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.assigner = None
		self.attempts = {}
		self.sql_fetcher = SqlFetcher(os.path.join("modules", "join", "queries"))

	@commands.Cog.listener()
	async def on_ready(self):
		self.assigner = Assigner(config.guild, config.conn, self.sql_fetcher)

	@commands.command(name="join")
	@commands.has_role(utils.get_id("UNASSIGNED_ROLE"))
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
					f"\n\n{utils.get_discord_obj(ctx.guild.roles, 'ADMIN_ROLE').mention}"
					f" Help! {ctx.author.mention} doesn't seem to be able to read"
					" instructions."
				)
			self.attempts[ctx.author] += 1
			raise FriendlyError(err_msg, ctx.channel, ctx.author)

	@cog_ext.cog_slash(
		name="join",
		description="Join command to get new users' information and place them in the right roles.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="first_name",
				description="Your first name",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="last_name",
				description="Your last name",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="campus",
				description="Your campus (Lev or Tal)",
				option_type=SlashCommandOptionType.STRING,
				required=True,
				choices=[
					create_choice(name="Lev", value="Lev"),
					create_choice(name="Tal", value="Tal"),
				],
			),
			create_option(
				name="year",
				description="Your year (an integer 1 to 4 inclusive)",
				option_type=SlashCommandOptionType.INTEGER,
				required=True,
				choices=[
					create_choice(name="Year 1", value=1),
					create_choice(name="Year 2", value=2),
					create_choice(name="Year 3", value=3),
					create_choice(name="Year 4", value=4),
				],
			),
		],
	)
	async def _join(
		self, ctx: SlashContext, first_name: str, last_name: str, campus: str, year: int
	):
		await self.assigner.assign(
			ctx.author, f"{first_name.title()} {last_name.title()}", campus, year
		)
		await ctx.send(
			embeds=[
				utils.embed_success(
					title=f"**{ctx.author.display_name}** used **/{ctx.invoked_with}**"
				)
			]
		)


# setup functions for bot
def setup(bot: commands.Bot):
	bot.add_cog(JoinCog(bot))
