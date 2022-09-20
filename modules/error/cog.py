import config
import sys
from .friendly_error import FriendlyError
from utils import utils
from nextcord.ext import commands
import nextcord
from .error_handler import ErrorHandler
from .error_logger import ErrorLogger


class ErrorLogCog(commands.Cog):
	"""Show recent error logs"""

	def __init__(self, bot: commands.Bot):
		self.logger = ErrorLogger("err.log", utils.get_id("BOT_LOG_CHANNEL"))
		self.handler = ErrorHandler(self.logger)

		@bot.event
		async def on_error(event: str, *args, **kwargs):
			_, error, _ = sys.exc_info()
			if error:
				await self.handler.handle(error)

		@bot.event
		async def on_application_command_error(
			interaction: nextcord.Interaction, error: Exception
		):
			await self.handler.handle(error, interaction.message)

	@nextcord.slash_command(name="logs", guild_ids=[config.guild_id])
	async def logs(self, interaction: nextcord.Interaction, num_lines: int = 50):
		"""Show recent logs from err.log."""
		await interaction.send(self.logger.read_logs(num_lines))


# setup functions for bot
def setup(bot: commands.Bot):
	# We need to pass the bot to the cog
	# so that we can set up the listeners
	# within the cog. This enables us to
	# use the cog's methods in the listeners
	cog = ErrorLogCog(bot)
	bot.add_cog(cog)