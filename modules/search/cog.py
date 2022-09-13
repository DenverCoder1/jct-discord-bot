from typing import List
from ..error.friendly_error import FriendlyError
from nextcord.ext import commands
import nextcord
from googlesearch import search
import modules.search.search_functions as sf
import config


class SearchCog(commands.Cog):
	"""Searches Google for links and includes summaries from Wikipedia when relevant"""

	def __init__(self, bot):
		self.bot = bot
		self.last_paragraph = {}

	@nextcord.slash_command(name="search", guild_ids=[config.guild_id])
	async def search(self, interaction: nextcord.Interaction, query: str):
		"""Search the web for anything you want."""
		if query == "who asked":
			await interaction.send(
				"After a long and arduous search, I have found the answer to your"
				" question: Nobody. Nobody asked."
			)
			return
		await interaction.response.defer()
		links: List[str] = [link for link in search(query) if link.startswith("http")]
		if not links:
			raise FriendlyError("No results found", interaction)
		wiki_links = [link for link in links if "wikipedia.org" in link[:30]]
		wiki_intro = (
			sf.get_wiki_intro(wiki_links[0])
			if wiki_links and wiki_links[0] != links[0]
			else None
		)
		await interaction.send(sf.format_message(query, links[0], wiki_intro))


# setup functions for bot
def setup(bot):
	bot.add_cog(SearchCog(bot))