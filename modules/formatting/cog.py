from discord.ext import commands
from .tip_formatter import TipFormatter


class FormattingCog(commands.Cog, name="Formatting Tips"):
	"""Display markdown tips for Discord messages"""
	def __init__(self, bot):
		self.bot = bot
		self.tips = TipFormatter()

	@commands.command(name="markdown", aliases=["md"])
	async def markdown(self, ctx, *args):
		"""
		Command to display markdown tips for Discord messages.

		Usage:
		```
		++md [format]
		```
		Arguments:

			> **format** (optional): The format to display information about (ex. "bold", "italics", "codeblock", ...)

		If no argument is specified, all markdown tips will be displayed.
		"""
		if len(args) == 0:
			message = self.tips.all_markdown_tips()
			await ctx.send(message)
		else:
			message = self.tips.individual_info(ctx, "".join(args))
			await ctx.send(message)


# setup functions for bot
def setup(bot):
	bot.add_cog(FormattingCog(bot))