import config
import sys
from utils import utils
from nextcord.ext import commands
import nextcord
from .error_handler import ErrorHandler
from .error_logger import ErrorLogger


class ErrorLogCog(commands.Cog):
	"""Show recent error logs"""

	def __init__(self):
		self.logger = ErrorLogger("err.log", utils.get_id("BOT_LOG_CHANNEL"))
		self.handler = ErrorHandler(self.logger)

	@nextcord.slash_command(name="logs", guild_ids=[config.guild_id])
	async def logs(self, interaction: nextcord.Interaction, num_lines: int = 50):
		"""Show recent logs from err.log."""
		await interaction.send(self.logger.read_logs(num_lines))

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: Exception):
		"""When a command exception is raised, log it in err.log and bot log channel"""
		await self.handler.handle(error, ctx.message)

	@commands.Cog.listener()
	async def on_slash_command_error(self, interaction: nextcord.Interaction, error: Exception):
		"""When a slash exception is raised, log it in err.log and bot log channel"""
		await self.handler.handle(error, interaction.message)

	@commands.Cog.listener()
	async def on_error(self, event, *args, **kwargs):
		"""When an exception is raised, log it in err.log and bot log channel"""

		_, error, _ = sys.exc_info()
		if error:
			await self.handler.handle(error)


# setup functions for bot
def setup(bot: commands.Bot):
	cog = ErrorLogCog()
	bot.add_cog(cog)
	setattr(bot, "on_error", cog.on_error)