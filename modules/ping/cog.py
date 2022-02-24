from nextcord.ext import commands
import os
import config
import random
import getpass
import socket


class PingCog(commands.Cog):
	"""A command which simply acknowledges the user's ping"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		with open(os.path.join("modules", "ping", "responses.txt")) as responses:
			self.lines = responses.readlines()

	@cog_ext.cog_slash(
		name="ping",
		description="A command which simply acknowledges the user's ping.",
		guild_ids=[config.guild_id],
	)
	async def ping(self, interaction: nextcord.Interaction):
		# log in console that a ping was received
		print("Received ping")
		await ctx.send(
			f"**{getpass.getuser()} @ {socket.gethostname()} $**"
			f" {random.choice(self.lines)}"
		)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(PingCog(bot))
