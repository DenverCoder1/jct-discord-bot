from typing import Optional
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from .xkcd_fetcher import XKCDFetcher
from .xkcd_embedder import XKCDEmbedder
from discord.ext import commands
import config


class XKCDCog(commands.Cog, name="xkcd Comics"):
	"""Displays the latest xkcd comic, random comics, or comics for your search terms"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.xkcd_fetcher = XKCDFetcher()
		self.xkcd_embedder = XKCDEmbedder()

	@cog_ext.cog_subcommand(
		base="xkcd",
		name="get",
		description="Get a random xkcd comic or one you specify.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="comic_id",
				description=(
					"The id of the xkcd comic you want to get. (eg. 221) (default is"
					" random)"
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
			)
		],
	)
	async def xkcd(self, ctx: SlashContext, comic_id: Optional[int] = None):
		await ctx.defer()
		comic = (
			self.xkcd_fetcher.get_comic_by_id(comic_id)
			if comic_id
			else self.xkcd_fetcher.get_random()
		)
		await ctx.send(embed=self.xkcd_embedder.gen_embed(comic))

	@cog_ext.cog_subcommand(
		base="xkcd",
		name="latest",
		description="Get the latest xkcd comix.",
		guild_ids=[config.guild_id],
	)
	async def xkcd_latest(self, ctx: SlashContext):
		await ctx.defer()
		comic = self.xkcd_fetcher.get_latest()
		await ctx.send(embed=self.xkcd_embedder.gen_embed(comic))

	@cog_ext.cog_subcommand(
		base="xkcd",
		name="search",
		description="Search for an xkcd comic",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="query",
				description="Your search terms",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			)
		],
	)
	async def xkcd_search(self, ctx: SlashContext, query: str):
		await ctx.defer()
		comic = self.xkcd_fetcher.search_relevant(query)
		await ctx.send(embed=self.xkcd_embedder.gen_embed(comic))


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
