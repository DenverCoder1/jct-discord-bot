from modules.teacher_emails.email_crud import EmailCrud
from discord.ext import commands
import config


class TeacherEmailsCog(commands.Cog, name="Teacher Emails"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.crud = EmailCrud(config.conn)

	@commands.command(name="getemail", aliases=["get email", "emailof", "email of"])
	async def get_email(self, ctx: commands.Context, *args):
		"""This command returns the email address of the teacher you ask for

		Usage:
		```
		++getemail query
		```
		Arguments:
		> **query**: A string which contains the professor's name and/or any of the subjects they teach (e.g. eitan computer science)
		"""
		profs = self.crud.search(" ".join(args))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(TeacherEmailsCog(bot))