from datetime import datetime

from discord import channel
from modules.error.friendly_error import FriendlyError
import traceback
import discord


class ErrorLogger:
	def __init__(self, log_file: str, log_channel_id: int) -> None:
		self.log_file = log_file
		self.log_channel_id = log_channel_id

	def log_to_file(self, error: Exception, message: discord.Message):
		"""appends the date and logs text to a file"""
		with open(self.log_file, "a", encoding="utf-8") as f:
			# write the current time and log text at end of file
			f.write(str(datetime.now()) + "\n")
			f.write(self.__get_err_text(error, message) + "\n")
			f.write("--------------------------\n")

	async def log_to_channel(self, error: Exception, message: discord.Message):
		log_channel = message.guild.get_channel(self.log_channel_id)
		await log_channel.send(
			f"Error triggered by {message.author.mention} in"
			f" {message.channel.mention}\n```{self.__get_err_text(error, message)}```"
		)

	def __get_err_text(self, error: Exception, message: discord.Message):
		trace = traceback.format_exc()
		description = trace if trace != "NoneType: None\n" else str(error)
		return self.__attach_context(description, message)

	def __attach_context(self, description: str, message: discord.Message):
		"""returns human readable command error for logging in log channel"""
		return (
			f"Author:\n{message.author} ({message.author.display_name})\n\n"
			f"Channel:\n{message.channel}\n\n"
			f"Message:\n{message.content}\n\n"
			f"Error:\n{description}\n"
		)

	def read_logs(self, n_lines: int = 50, char_lim: int = 2000) -> str:
		with open(self.log_file, "r", encoding="utf-8") as f:
			# read logs file
			lines = f.readlines()
			last_n_lines = "".join(lines[-n_lines:])
			# trim the logs if too long
			if len(last_n_lines) > char_lim - 10:
				last_n_lines = f"․․․\n{last_n_lines[-(char_lim - 10):]}"
			return f"```{last_n_lines}```"