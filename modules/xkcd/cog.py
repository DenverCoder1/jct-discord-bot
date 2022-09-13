from typing import Optional
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

	@nextcord.command(name="xkcd")
	async def xkcd(self, interaction: nextcord.Interaction):
		"""This is a base command for all xkcd commands and is not invoked"""
		pass

	@xkcd.subcommand(name="latest", description="Displays the latest xkcd comic")
	async def latest(self, interaction: nextcord.Interaction):
		"""Displays the latest xkcd comic"""
		interaction.response.defer()
		try:
			comic = await self.xkcd_fetcher.get_latest()
		except ConnectionError as e:
			interaction.response.send_message(e, ephemeral=True)
			return

		await interaction.response.send_message(
			embed=self.xkcd_embedder.gen_embed(comic)
		)

	@xkcd.subcommand(name="random", description="Displays a random xkcd comic")
	async def random(self, interaction: nextcord.Interaction):
		"""Displays a random xkcd comic"""
		interaction.response.defer()
		comic = await self.xkcd_fetcher.get_random()
		await interaction.response.send_message(
			embed=self.xkcd_embedder.gen_embed(comic)
		)

	@xkcd.subcommand(name="get", description="Gets a specific xkcd comic")
	async def get(
		self,
		interaction: nextcord.Interaction,
		number: int = nextcord.SlashOption(
			description="The number of the comic to display"
		),
	):
		"""Displays an xkcd comic by number"""
		interaction.response.defer()
		try:
			comic = await self.xkcd_fetcher.get_comic_by_id(number)
		except ConnectionError as e:
			await interaction.response.send_message(e, ephemeral=True)
			return
		await interaction.response.send_message(
			embed=self.xkcd_embedder.gen_embed(comic)
		)

	@xkcd.subcommand(name="search", description="Searches for a relevant xkcd comic")
	async def search(self, interaction: nextcord.Interaction, query: str):
		"""Searches for a relevant xkcd comic"""
		interaction.response.defer()
		try:
			comic = await self.xkcd_fetcher.search_relevant(query)
		except ConnectionError as e:
			await interaction.response.send_message(e, ephemeral=True)
			return
		await interaction.response.send_message(
			embed=self.xkcd_embedder.gen_embed(comic)
		)


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
