import asyncio
from database import preloaded
from database.campus import Campus
from utils import embedder, utils
from . import assigner
from nextcord.ext import commands
import config


class JoinCog(commands.Cog):
	"""Join command to get new users information and place them in the right roles"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.assigner = None

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
				option_type=SlashCommandOptionType.STRING,
				required=True,
				choices=[
					create_choice(name=campus.name, value=str(campus.id))
					for campus in preloaded.campuses
				],
			),
			create_option(
				name="year",
				description="Your year",
				option_type=SlashCommandOptionType.STRING,
				required=True,
				choices=[
					create_choice(name=f"Year {i}", value=str(i)) for i in range(1, 5)
				],
			),
		],
	)
	@commands.has_role(utils.get_id("UNASSIGNED_ROLE"))
	async def join(
		self,
		interaction: nextcord.Interaction,
		first_name: str,
		last_name: str,
		campus: str,
		year: str,
	):
		# TODO: campus and year should really take integer options, but mobile has a bug
		await ctx.defer()
		await assigner.assign(
			ctx.author,
			f"{first_name.title()} {last_name.title()}",
			int(campus),
			int(year),
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
