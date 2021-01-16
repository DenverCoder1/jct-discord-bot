import discord
import config
from modules.error.error_logger import ErrorLogger
from modules.error.friendly_error import FriendlyError
import discord.ext.commands.errors as discord_err


class ErrorHandler:
	"""
	Class that handles raised exceptions
	"""

	def __init__(self, error_logger: ErrorLogger) -> None:
		self.logger = error_logger

	async def handle(self, error: Exception, message: discord.Message = None):
		if isinstance(error, FriendlyError):
			await self.__handle_friendly(error, message)

		elif isinstance(error, discord_err.CommandInvokeError):
			await self.handle(error.original, message)

		else:
			self.logger.log_to_file(error, message)
			await self.logger.log_to_channel(error, message)
			if message is not None:
				friendly_err = FriendlyError(
					self.__user_error_message(error),
					message.channel,
					message.author,
					error,
				)
				await self.handle(friendly_err, message)

	async def __handle_friendly(
		self, error: FriendlyError, message: discord.Message = None
	):
		if error.inner is not None:
			self.logger.log_to_file(error.inner, message)
		await error.reply()

	def __user_error_message(self, error: Exception):
		if isinstance(error, discord_err.CommandNotFound):
			return (
				"That command does not exist. Check your spelling or see all available"
				f" commands with `{config.prefix}help`"
			)
		elif isinstance(error, discord_err.MissingRequiredArgument):
			return f"Argument {error.param} required."
		elif isinstance(error, discord_err.TooManyArguments):
			return f"Too many arguments given."
		elif isinstance(error, discord_err.BadArgument):
			return f"Bad argument: {error}"
		elif isinstance(error, discord_err.NoPrivateMessage):
			return f"That command cannot be used in DMs."
		elif isinstance(error, discord_err.MissingPermissions):
			return (
				"You are missing the following permissions required to run the"
				f' command: {", ".join(error.missing_perms)}.'
			)
		elif isinstance(error, discord_err.DisabledCommand):
			return f"That command is disabled or under maintenance."
		elif isinstance(error, discord_err.CommandInvokeError):
			return f"Error while executing the command."
		else:
			return f"An unknown error occurred."
