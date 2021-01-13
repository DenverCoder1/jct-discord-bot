import sys
import utils.utils as utils
from discord.ext import commands
from modules.error.error_handler import ErrorHandler
from modules.error.error_logger import ErrorLogger


class ErrorLogCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.logger = ErrorLogger("err.log", utils.get_id("BOT_LOG_CHANNEL_ID"))
		self.handler = ErrorHandler(self.logger)

	@commands.command(name="logs")
	async def logs(self, ctx: commands.Context, num_lines: int = 50):
		"""Show recent logs from err.log"""
		# log in console that a ping was received
		print('Executing command "logs".')
		# send the logs
		await ctx.send(self.logger.read_logs(num_lines))

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: Exception):
		"""When a command exception is raised, log it in err.log and bot log channel"""
		await self.handler.handle(error, ctx.message)


async def on_error(self, event, *args, **kwargs):
	"""When an exception is raised, log it in err.log and bot log channel"""
	_, error, _ = sys.exc_info()
	# error while handling message
	if event in [
		"message",
		"on_message",
		"message_discarded",
		"on_message_discarded",
		"on_command_error",
	]:
		msg = f"**Error while handling a message**"
		await ErrorHandler(args[0], error, msg).handle_error()
	# other errors
	else:
		msg = f"An error occurred during an event and was not reported: {event}"
		await ErrorHandler("", error, msg).handle_error()


# setup functions for bot
def setup(bot: commands.Bot):
	bot.add_cog(ErrorLogCog(bot))
	bot.on_error = on_error