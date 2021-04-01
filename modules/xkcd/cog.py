from .xkcd_fetcher import XKCDFetcher
from .xkcd_embedder import XKCDEmbedder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands


class XKCDCog(commands.Cog, name="XKCD Comics"):
	"""Displays the latest xkcd comic, random comics, or comics for your search terms"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.xkcd_fetcher = XKCDFetcher()
		self.xkcd_embedder = XKCDEmbedder()

	@commands.command(name="xkcd")
	async def xkcd(self, ctx: commands.Context, *args):
		"""Displays the latest xkcd comic, random comics, or comics for your search terms

		Usage:

		`++xkcd` - displays a random xkcd comic

		`++xkcd latest` - displays the latest xkcd comic

		`++xkcd [number]` - displays an xkcd comic given its id (eg. `++xkcd 327`)

		`++xkcd [search term]` - displays a comic for your search term (eg. `++xkcd sql`)
		"""

		search = " ".join(args).lower()

		try:
			# ++xkcd latest
			if search == "latest":
				# get the latest xkcd comic
				comic = self.xkcd_fetcher.get_latest()
			# ++xkcd [num]
			elif search.isdigit():
				# get response from the xkcd API with search as the id
				comic = self.xkcd_fetcher.get_comic_by_id(int(search))
			# ++xkcd [search term]
			elif len(args) > 0:
				# get relevant xkcd for search term
				comic = self.xkcd_fetcher.search_relevant(search)
			# ++xkcd
			else:
				# get a random xkcd comic
				comic = self.xkcd_fetcher.get_random()
			# embed the response
			embed = self.xkcd_embedder.gen_embed(comic)
			# reply with the embed
			await ctx.send(embed=embed)
		except ConnectionError as error:
			# request did not return a 200 response code
			raise FriendlyError(error.args[0], ctx.channel, ctx.message.author, error)


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))
