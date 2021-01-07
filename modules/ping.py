from discord.ext import commands

class Ping(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(name='ping')
	async def ping(self, ctx):
		"""A simple command which acknowledges the user's ping."""

		# log in console that a ping was received
		print('Received ping')

		await ctx.send('Leave me alone, I\'m trying to sleep.')


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot):
	bot.add_cog(Ping(bot))