from modules.teacher_emails.professor_embedder import ProfessorEmbedder
from modules.teacher_emails.email_finder import EmailFinder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands
import config


class TeacherEmailsCog(commands.Cog, name="Teacher Emails"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = EmailFinder(config.conn)
		self.embedder = ProfessorEmbedder()

	@commands.command(name="getemail", aliases=["email", "emailof"])
	async def get_email(self, ctx: commands.Context, *args):
		"""This command returns the email address of the teacher you ask for

		Usage:
		```
		++getemail query
		```
		Arguments:
		> **query**: A string which contains the professor's name and/or any of the subjects they teach (e.g. eitan computer science)
		"""
		profs = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		if not profs:
			raise FriendlyError("Sorry, no professors were found.", ctx.channel)
		else:
			title = (
				"**_YOU_ get an email!! _YOU_ get an email!!**\nEveryone gets an email!"
			)
			embed = self.embedder.gen_embed(profs)
			await ctx.send(content=title, embed=embed)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(TeacherEmailsCog(bot))