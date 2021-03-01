import sys
from utils import utils
from discord.ext import commands
from modules.error.error_handler import ErrorHandler
from modules.error.error_logger import ErrorLogger


class ErrorLogCog(commands.Cog, name="Error Logs"):
	"""Show recent error logs"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.logger = ErrorLogger("err.log", utils.get_id("BOT_LOG_CHANNEL"), bot)
		self.handler = ErrorHandler(self.logger)

	@commands.command(name="logs")
	async def logs(self, ctx: commands.Context, num_lines: int = 50):
		"""Show recent logs from err.log

		Usage:
		```
		++logs
		```
		"""
		# log in console that a ping was received
		print('Executing command "logs".')
		# send the logs
		await ctx.send(self.logger.read_logs(num_lines))

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: Exception):
		"""When a command exception is raised, log it in err.log and bot log channel"""
		await self.handler.handle(error, ctx.message)

	@commands.Cog.listener()
	async def on_error(self, event, *args, **kwargs):
		"""When an exception is raised, log it in err.log and bot log channel"""

		_, error, _ = sys.exc_info()
		await self.handler.handle(error)


# setup functions for bot
def setup(bot: commands.Bot):
	cog = ErrorLogCog(bot)
	bot.add_cog(cog)
	bot.on_error = cog.on_error