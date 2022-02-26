from typing import List
from ..error.friendly_error import FriendlyError
from nextcord.ext import commands
from googlesearch import search
import modules.search.search_functions as sf
import config
import nextcord
from nextcord import SlashOption


class SearchCog(commands.Cog):
	"""Searches Google for links and includes summaries from Wikipedia when relevant"""

	def __init__(self, bot):
		self.bot = bot
		self.last_paragraph = {}

	@nextcord.slash_command(
		name="search",
		description="Search the web for anything you want.",
		guild_ids=[config.guild_id],
	)
	async def search(
		self,
		interaction: nextcord.Interaction,
		query: str = SlashOption(description="Your search query", required=True),
	):
		await interaction.response.defer()

		links: List[str] = [link for link in search(query) if link.startswith("http")]
		if not links:
			raise FriendlyError(
				"We searched far and wide, but nothing turned up.", interaction.send
			)

		wiki_links = [link for link in links if "wikipedia.org" in link[:30]]
		wiki_intro = (
			sf.get_wiki_intro(wiki_links[0])
			if wiki_links and wiki_links[0] != links[0]
			else None
		)

		await interaction.send(content=sf.format_message(query, links[0], wiki_intro))


# setup functions for bot
def setup(bot):
	bot.add_cog(SearchCog(bot))