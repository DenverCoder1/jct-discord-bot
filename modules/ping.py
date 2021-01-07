from discord.ext import commands
import random

class Ping(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(name='ping')
	async def ping(self, ctx):
		"""A simple command which acknowledges the user's ping."""

		# log in console that a ping was received
		print('Received ping')

		responses = [
			'Leave me alone, I\'m trying to sleep',
			'Waaaazzzzzzzzaaaaaaaaaappppppp',
			'Who do you think you are, puny human, to be pinging me?',
			'Pong',
			'Hey',
			'This is *not* the droid you are looking for :hand_splayed:'
		]

		await ctx.send(random.choice(responses))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot):
	bot.add_cog(Ping(bot))
