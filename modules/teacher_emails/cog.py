import discord
from modules.teacher_emails.professor_embedder import ProfessorEmbedder
from modules.teacher_emails.email_finder import EmailFinder
from modules.teacher_emails.email_adder import EmailAdder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands
import config


class TeacherEmailsCog(commands.Cog, name="Teacher Emails"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = EmailFinder(config.conn)
		self.embedder = ProfessorEmbedder()
		self.adder = EmailAdder(config.conn)

	@commands.command(name="getemail", aliases=["email", "emailof"])
	async def get_email(self, ctx: commands.Context, *args):
		"""This command returns the email address of the teacher you ask for.

		Usage:
		```
		++getemail query
		```
		Arguments:
		> **query**: A string with the professor's name and/or any courses they teach (or their channels) (e.g. eitan computer science)
		"""
		profs = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		profs = {prof for prof in profs if prof.emails}
		if not profs:
			raise FriendlyError(
				"The email you are looking for aught to be here... But it isn't."
				" Perhaps the archives are incomplete.",
				ctx.channel,
			)
		else:
			title = (
				"**_YOU_ get an email!! _YOU_ get an email!!**\nEveryone gets an email!"
			)
			embed = self.embedder.gen_embed(profs)
			await ctx.send(content=title, embed=embed)

	@commands.command(name="addemail")
	async def add_email(self, ctx: commands.Context, *args):
		"""Add the email of a professor with this command.

		Usage:
		```
		++addemail query emails
		```
		Arguments:
		> **query**: A string to identify a teacher. Must be specific enough to match a single teacher. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **emails**: One or more of the teacher's email addresses
		"""
		# search for professor's details
		profs = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		if not profs:
			raise FriendlyError(
				"Unable to find a professor to match your query.", ctx.channel
			)
		if len(profs) > 1:
			raise FriendlyError(
				"I cannot accurately determine which of these professors you're"
				" referring to. Please provide a more specific query.\n"
				+ ", ".join(prof.name for prof in profs),
				ctx.channel,
			)
		# add the emails to the database
		self.adder.add_emails(next(iter(profs)), self.adder.filter_emails(args))
		# update professors set from database
		profs = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		await ctx.send(embed=self.embedder.gen_embed(profs))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(TeacherEmailsCog(bot))
