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
	async def xkcd(self, interaction: nextcord.Interaction):
		"""This is a base command for all xkcd commands and is not invoked"""
		pass

	@xkcd.subcommand(name="latest")
	async def latest(self, interaction: nextcord.Interaction):
		"""Displays the latest xkcd comic"""
		await interaction.response.defer()
		comic = self.xkcd_fetcher.get_latest()
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="random")
	async def random(self, interaction: nextcord.Interaction):
		"""Displays a random xkcd comic"""
		await interaction.response.defer()
		comic = self.xkcd_fetcher.get_random()
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="get")
	async def get(
		self,
		interaction: nextcord.Interaction,
		number: int = nextcord.SlashOption(
			description="The number of the comic to display"
		),
	):
		"""Gets a specific xkcd comic"""
		await interaction.response.defer()
		comic = self.xkcd_fetcher.get_comic_by_id(number)
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))

	@xkcd.subcommand(name="search")
	async def search(self, interaction: nextcord.Interaction, query: str):
		"""Searches for a relevant xkcd comic"""
		await interaction.response.defer()
		comic = self.xkcd_fetcher.search_relevant(query)
		await interaction.send(embed=self.xkcd_embedder.gen_embed(comic))


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
