import requests
from modules.error.friendly_error import FriendlyError
from discord.ext import commands

class XKCDFetcher:
	def fetch(self, id: int, ctx: commands.Context) -> dict:
		response = requests.get(f"https://xkcd.com/{id}/info.0.json")
		if response.status_code != 200:
			# XKCD API did not return a 200 response code
			raise FriendlyError(
				"Could not find a comic with that id.",
				ctx.channel
			)
		# load json from response
		return response.json()