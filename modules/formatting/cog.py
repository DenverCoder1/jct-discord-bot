from discord.ext import commands
from .formatting_tips import FormattingTips


class FormattingCog(commands.Cog, name="Formatting Tips"):
	def __init__(self, bot):
		self.bot = bot
		self.tips = FormattingTips()

	@commands.command(name="markdown")
	async def markdown(self, ctx):
		"""Replies with a summary of basic markdown supported by Discord."""
		await ctx.send(self.tips.markdown_info())

	@commands.command(name="codeblock")
	async def codeblock(self, ctx):
		"""Replies with a summary of how to format code with codeblocks."""
		await ctx.send(self.tips.codeblock_info())


# setup functions for bot
def setup(bot):
	bot.add_cog(FormattingCog(bot))