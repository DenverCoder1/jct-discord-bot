from modules.error.friendly_error import FriendlyError
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from googlesearch import search
import modules.search.search_functions as sf
import config


class SearchCog(commands.Cog, name="Search"):
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
		await ctx.defer()

		links = search(query)
		if not links:
			raise FriendlyError("We searched far and wide, but nothing turned up.", ctx)
		link = links[0]

		wiki_links = [link for link in links if "wikipedia.org" in link[:30]]
		wiki_intro = (
			sf.get_wiki_intro(wiki_links[0])
			if wiki_links and wiki_links[0] != link
			else None
		)

		await ctx.send(content=sf.format_message(query, links[0], wiki_intro))


# setup functions for bot
def setup(bot):
	bot.add_cog(SearchCog(bot))