from database.campus.campus import Campus
from utils import embedder, utils
from modules.join.assigner import Assigner
from discord.ext import commands
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

	@commands.Cog.listener()
	async def on_ready(self):
		self.assigner = Assigner(config.guild, config.conn)

	@cog_ext.cog_slash(
		name="join",
		description=(
			"Join command to get new users' information and place them in the right"
			" roles."
		),
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
				option_type=SlashCommandOptionType.INTEGER,
				required=True,
				choices=[
					create_choice(name=campus.name, value=campus.campus_id)
					for campus in Campus.get_campuses()
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
	@commands.has_role(utils.get_id("UNASSIGNED_ROLE"))
	async def _join(
		self,
		ctx: SlashContext,
		first_name: str,
		last_name: str,
		campus_id: int,
		year: int,
	):
		await self.assigner.assign(
			ctx.author, f"{first_name.title()} {last_name.title()}", campus_id, year
		)
		await ctx.send(
			embeds=[
				embedder.embed_success(
					title=f"**{ctx.author.display_name}** used **/{ctx.invoked_with}**"
				)
			]
		)


# setup functions for bot
def setup(bot: commands.Bot):
	bot.add_cog(JoinCog(bot))
