from modules.piglatin.translate import translate
from discord.ext import commands


class PigLatin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="piglatin")
	async def piglatin(self, ctx, *args):
		"""Will convert message to pig latin."""

		# log in console that a ping was received
		print('Executing command "piglatin".')

		# reply with a message
		await ctx.send(translate(" ".join(args)))


def setup(bot):
	bot.add_cog(PigLatin(bot))