from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
import config
import random


class PingCog(commands.Cog, name="Ping"):
	"""A command which simply acknowledges the user's ping"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		with open("modules/ping/responses.txt") as responses:
			self.lines = responses.readlines()

	@cog_ext.cog_slash(
		name="ping",
		description="A command which simply acknowledges the user's ping.",
		guild_ids=[config.guild_id],
	)
	async def ping(self, ctx: SlashContext):
		# log in console that a ping was received
		print("Received ping")
		await ctx.send(random.choice(self.lines))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(PingCog(bot))
