import traceback
from discord import logging
from discord.ext.commands.errors import *
from modules.utils.utils import get_discord_obj
from datetime import datetime


class ErrorHandler:
	"""
	Handles different types of error messages
	"""

	def __init__(self, message, error, human_details):
		self.message = message
		self.error = error
		self.human_details = human_details
		# formats the error as traceback
		self.trace = traceback.format_exc()
		# get the bot log channel
		self.log_channel = get_discord_obj(message.guild.channels, "BOT_LOG_CHANNEL_ID")

	async def handle_error(self):
		"""When an exception is raised, log it in err.log and bot log channel"""
		error_details = self.trace if self.trace != "NoneType: None\n" else self.error
		# logs error as warning in console
		logging.warning(error_details)
		# log to err.log
		self.__log_to_file("err.log", error_details)
		# notify user of error
		user_error = self.__user_error_message()
		await self.message.channel.send(user_error)
		# send formatted message in bot log channel
		log_channel_error = self.__attach_message_info(error_details)
		await self.send_in_log_channel(log_channel_error)

	async def send_in_log_channel(self, log_channel_error):
		await self.log_channel.send(log_channel_error)  # log error in bot log channel

	def __attach_message_info(self, error_details):
		"""returns human readable command error for logging in log channel"""
		msg = self.message if hasattr(self.message, "content") else self.message.message
		return (
			"Message info:\n```"
			f"Message author:\n{msg.author} ({msg.author.nick})\n\n"
			f"Message channel:\n{msg.channel}\n\n"
			f"Message content:\n{msg.content}```\n"
			f"Details:\n```{error_details}```\n"
		)

	def __user_error_message(self):
		if isinstance(self.error, CommandNotFound):
			return f"Command not found."
		elif isinstance(self.error, MissingRequiredArgument):
			return f"Argument {self.error.param} required."
		elif isinstance(self.error, TooManyArguments):
			return f"Too many arguments given."
		elif isinstance(self.error, BadArgument):
			return f"Bad argument: {self.error}"
		elif isinstance(self.error, NoPrivateMessage):
			return f"That command cannot be used in DMs."
		elif isinstance(self.error, MissingPermissions):
			return (
				"You are missing the following permissions required to run the"
				f' command: {", ".join(self.error.missing_perms)}.'
			)
		elif isinstance(self.error, DisabledCommand):
			return f"That command is disabled or under maintenance."
		elif isinstance(self.error, CommandInvokeError):
			return f"Error while executing the command."
		else:
			return f"An unknown error occurred."

	def __log_to_file(self, filename: str, text: str):
		"""appends the date and logs text to a file"""
		with open(filename, "a", encoding="utf-8") as f:
			# write the current time and log text at end of file
			f.write(f"{datetime.now()}\n{text}\n------------------------------------\n")
