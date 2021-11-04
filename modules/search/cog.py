from typing import List
from ..error.friendly_error import FriendlyError
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
import modules.search.wiki_functions as wf
from .bing_snippet_functions import get_question_snippet
from .formatting import  format_message
import config

class SearchCog(commands.Cog):
	"""Searches Google for links and includes summaries from Wikipedia when relevant"""

	def __init__(self, bot):
		self.bot = bot
		self.last_paragraph = {}

	@cog_ext.cog_slash(
		name="search",
		description="Search the web for anything you want.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="query",
				description="Your search query",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
		],
	)
	async def search(self, ctx: SlashContext, query: str):
		"""Sends a message with a relavant search result from Bing"""
		await ctx.defer()

		snippet = get_question_snippet(query)
		
		if (snippet == None):
			links: List[str] = [link for link in search(query) if link.startswith("http")]
			if not links:
				raise FriendlyError("We searched far and wide, but nothing turned up.", ctx)

			wiki_links = [link for link in links if "wikipedia.org" in link[:30]]
			wiki_intro = (
				wf.get_wiki_intro(wiki_links[0])
				if wiki_links and wiki_links[0] != links[0]
				else None
			)

			await ctx.send(content=format_message(query, links[0], wiki_intro))

		await ctx.send(content=snippet)


# setup functions for bot
def setup(bot):
	bot.add_cog(SearchCog(bot))