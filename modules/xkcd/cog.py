from .xkcd_fetcher import XKCDFetcher
from .xkcd_embedder import XKCDEmbedder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands


class XKCDCog(commands.Cog, name="XKCD"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.xkcd_fetcher = XKCDFetcher()
		self.xkcd_embedder = XKCDEmbedder()

	@commands.command(name="xkcd")
	async def xkcd(self, ctx: commands.Context, *args):
		"""Displays the latest XKCD comic, a random comic, or a comic given its id.

		Usage:
		```
		++xkcd 327
		```
		Arguments:

			> **327**: Replace this with one of "latest", "random", or the comic id of an XKCD comic. \
			If no argument is provided, a random XKCD comic will be displayed.
		"""
		
		search = " ".join(args).lower()

		try:
			# ++xkcd latest
			if search == "latest":
				# get the latest XKCD comic
				json = self.xkcd_fetcher.get_latest()
			# ++xkcd [num]
			elif search.isdigit():
				# get response from the XKCD API with search as the id
				json = self.xkcd_fetcher.get_comic_by_id(int(search))
			# ++xkcd [search term]
			elif len(args) > 0:
				# get relevant xkcd for search term
				json = self.xkcd_fetcher.search_relevant(search)
			# ++xkcd
			else:
				# get a random XKCD comic
				json = self.xkcd_fetcher.get_random()
			# embed the response
			embed = self.xkcd_embedder.gen_embed(json)
			# reply with the embed
			await ctx.send(embed=embed)
		except ConnectionError as error:
			# request did not return a 200 response code
			raise FriendlyError(error.args[0], ctx.channel, ctx.message.author, error)


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
