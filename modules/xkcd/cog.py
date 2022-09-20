from ..error.friendly_error import FriendlyError
from .xkcd_fetcher import XKCDFetcher
from .xkcd_embedder import XKCDEmbedder
from nextcord.ext import commands
import config
import nextcord


class XKCDCog(commands.Cog):
	"""Displays the latest xkcd comic, random comics, or comics for your search terms"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.xkcd_fetcher = XKCDFetcher()
		self.xkcd_embedder = XKCDEmbedder()

	@nextcord.slash_command(name="xkcd", guild_ids=[config.guild_id])
	async def xkcd(self, interaction: nextcord.Interaction[commands.Bot]):
		"""This is a base command for all xkcd commands and is not invoked"""
		pass

	@xkcd.subcommand(name="latest")
	async def latest(self, interaction: nextcord.Interaction[commands.Bot]):
		"""Displays the latest xkcd comic"""
		await interaction.response.defer()
		try:
			comic = self.xkcd_fetcher.get_latest()
		except ConnectionError as e:
			raise FriendlyError(
				e.args[0],
				interaction,
				inner=e,
				description="Please try again later.",
			)
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="random")
	async def random(self, interaction: nextcord.Interaction[commands.Bot]):
		"""Displays a random xkcd comic"""
		await interaction.response.defer()
		try:
			comic = self.xkcd_fetcher.get_random()
		except ConnectionError as e:
			raise FriendlyError(
				e.args[0],
				interaction,
				inner=e,
				description="Please try again later.",
			)
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="get")
	async def get(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		number: int = nextcord.SlashOption(name="id"),
	):
		"""Gets a specific xkcd comic
		
		Args:
			number: The ID of the comic to display
		"""
		await interaction.response.defer()
		try:
			comic = self.xkcd_fetcher.get_comic_by_id(number)
		except ConnectionError as e:
			raise FriendlyError(
				e.args[0],
				interaction,
				inner=e,
				description="Please try again later, or try a different comic.",
			)

		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="search")
	async def search(self, interaction: nextcord.Interaction[commands.Bot], query: str):
		"""Searches for a relevant xkcd comic

		Args:
			query: The query to search for
		"""
		await interaction.response.defer()
		try:
			comic = self.xkcd_fetcher.search_relevant(query)
		except ConnectionError as e:
			raise FriendlyError(
				e.args[0],
				interaction,
				inner=e,
				description="Please try again later.",
			)

		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
