from modules.piglatin.translate import translate
from discord.ext import commands


class PigLatinCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(name="piglatin")
	async def piglatin(self, ctx: commands.Context, *args):
		"""Will convert message to pig latin."""

		# log in console that a ping was received
		print('Executing command "piglatin".')

		# reply with a message
		await ctx.send(translate(" ".join(args)))


def setup(bot: commands.Bot):
	bot.add_cog(PigLatinCog(bot))
