from .xkcd_fetcher import XKCDFetcher
from .xkcd_embedder import XKCDEmbedder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands


class XKCDCog(commands.Cog, name="XKCD"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.fetcher = XKCDFetcher()
		self.embedder = XKCDEmbedder()

	@commands.command(name="xkcd")
	async def xkcd(self, ctx: commands.Context, id: str):
		"""Displays an XKCD comic given its id.

		Usage:
		```
		++xkcd 327
		```
		Arguments:

			> **327**: Replace this with the comic id of the XKCD comic you wish to display.
		"""
		try:
			# extract digits from argument
			comic_id = int("".join(c for c in id if c.isdigit()))
			# get response from the XKCD API
			json = self.fetcher.fetch(comic_id, ctx)
			# embed the response
			embed = self.embedder.gen_embed(comic_id, json)
			# reply with the embed
			await ctx.send(embed=embed)
		except ValueError:
			# failed to find an integer in the argument
			raise FriendlyError(
				f"'{id}' could not be interpretted as a comic id.",
				ctx.channel
			)


def setup(bot: commands.Bot):
	bot.add_cog(XKCDCog(bot))