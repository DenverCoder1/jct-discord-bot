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
		
		comic_arg = "".join(args)

		try:
			# ++xkcd latest
			if comic_arg == "latest":
				# get the latest XKCD comic
				json = self.xkcd_fetcher.get_latest()
			# ++xkcd or ++xkcd random
			elif len(args) == 0 or comic_arg == "random":
				# get a random XKCD comic
				json = self.xkcd_fetcher.get_random()
			# ++xkcd [comic_id]
			else:
				# extract digits from argument
				comic_id = int("".join(c for c in comic_arg if c.isdigit()))
				# get response from the XKCD API
				json = self.xkcd_fetcher.get_comic_by_id(comic_id)
			# embed the response
			embed = self.xkcd_embedder.gen_embed(json)
			# reply with the embed
			await ctx.send(embed=embed)
		except ValueError:
			# failed to find an integer in the argument
			raise FriendlyError(
				f"'{comic_arg}' must be one of 'latest', 'random' or a comic id.",
				ctx.channel
			)
		except ConnectionError as error:
			# XKCD API did not return a 200 response code
			raise FriendlyError(error.args[0], ctx.channel)


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))