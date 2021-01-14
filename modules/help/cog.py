from discord.ext import commands
from .help_command import NewHelpCommand


class HelpCog(commands.Cog, name="Help"):
	def __init__(self, bot):
		self._original_help_command = bot.help_command
		bot.help_command = NewHelpCommand()
		bot.help_command.cog = self

	def cog_unload(self):
		self.bot.help_command = self._original_help_command


# setup functions for bot
def setup(bot):
	bot.add_cog(HelpCog(bot))