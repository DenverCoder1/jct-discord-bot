from modules.email_registry.person_embedder import PersonEmbedder
from modules.email_registry.email_finder import EmailFinder
from modules.email_registry.email_adder import EmailAdder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands
import config


class EmailRegistryCog(commands.Cog, name="Email Registry"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = EmailFinder(config.conn)
		self.embedder = PersonEmbedder()
		self.adder = EmailAdder(config.conn)

	@commands.command(name="getemail", aliases=["email", "emailof"])
	async def get_email(self, ctx: commands.Context, *args):
		"""This command returns the email address of the person you ask for.

		Usage:
		```
		++getemail query
		```
		Arguments:
		> **query**: A string with the professor's name and/or any courses they teach (or their channels) (e.g. eitan computer science)
		"""
		people = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		people = {person for person in people if person.emails}
		if not people:
			raise FriendlyError(
				"The email you are looking for aught to be here... But it isn't."
				" Perhaps the archives are incomplete.",
				ctx.channel,
			)
		else:
			title = (
				"**_YOU_ get an email!! _YOU_ get an email!!**\nEveryone gets an email!"
			)
			embed = self.embedder.gen_embed(people)
			await ctx.send(content=title, embed=embed)

	@commands.command(name="addemail")
	async def add_email(self, ctx: commands.Context, *args):
		"""Add the email of a professor with this command.

		Usage:
		```
		++addemail query emails
		```
		Arguments:
		> **query**: A string to identify a person. Must be specific enough to match a single person. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **emails**: One or more of the teacher's email addresses
		"""
		# search for professor's details
		people = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		if not people:
			raise FriendlyError(
				"Unable to find someone who matches your query. Check your spelling or"
				" try a different query. If you still can't find them, You can add"
				f" them with `{config.prefix}addperson`.",
				ctx.channel,
			)
		if len(people) > 1:
			raise FriendlyError(
				"I cannot accurately determine which of these people you're"
				" referring to. Please provide a more specific query.\n"
				+ ", ".join(person.name for person in people),
				ctx.channel,
			)
		# add the emails to the database
		self.adder.add_emails(next(iter(people)), self.adder.filter_emails(args))
		# update professors set from database
		people = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		await ctx.send(embed=self.embedder.gen_embed(people))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
