from modules.email_registry.categoriser import Categoriser
from modules.email_registry.person_embedder import PersonEmbedder
from modules.email_registry.person_finder import PersonFinder
from modules.email_registry.email_adder import EmailAdder
from modules.email_registry.person_adder import PersonAdder
from modules.error.friendly_error import FriendlyError
from modules.role_tag.member import Member
from discord.ext import commands
import config


class EmailRegistryCog(commands.Cog, name="Email Registry"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = PersonFinder(config.conn)
		self.embedder = PersonEmbedder()
		self.email_adder = EmailAdder(config.conn)
		self.person_adder = PersonAdder(config.conn)
		self.categoriser = Categoriser(config.conn)

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
		person = self.finder.search_one(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		# add the emails to the database
		self.email_adder.add_emails(person, self.email_adder.filter_emails(args))
		# update professors set from database
		people = self.finder.search(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		await ctx.send(embed=self.embedder.gen_embed(people))

	@commands.command(name="addperson")
	@commands.has_guild_permissions(manage_roles=True)
	async def add_person(self, ctx: commands.Context, *args):
		"""Add a faculty member to the email registry

		Usage:
		```
		++addperson @member channel-mentions
		```or
		```
		++addperson name surname channel-mentions
		```
		Arguments:
		> **@member**: A mention of the person you want to add, if they are in the server
		> **name**: The first name of the person you want to add (use quotes if it contains a space)
		> **surname**: The last name of the person you want to add
		> **channel-mentions**: A (possibly empty) space separated list of #channel-mentions which the professor teaches, or #ask-the-staff for a member of the administration
		"""
		if ctx.message.mentions:
			if len(ctx.message.mentions) > 1:
				raise FriendlyError("Please mention only one member.")
			full_name = Member(ctx.message.mentions[0]).base_name
			member_id = ctx.message.mentions[0].id
			name, surname = full_name.rsplit(" ", 1)
		else:
			name, surname = (s.strip() for s in args[0:2])
			member_id = None
			if "<" in {name[0], surname[0]}:
				raise FriendlyError(
					"The first two arguments must be a first name and a last name if"
					" you haven't mentioned the person you want to add."
				)
		self.person_adder.add_person(
			name, surname, ctx.message.channel_mentions, self.categoriser, member_id
		)

	@commands.command(name="categoriseperson", aliases=["categorizeperson"])
	@commands.has_guild_permissions(manage_roles=True)
	async def categorise_person(self, ctx: commands.Context, *args):
		"""Link a person to a category (for example a professor to a course they teach)

		Usage:
		```
		++categoriseperson query channel-mentions
		```
		Arguments:
		> **query**: A string to identify a person. Must be specific enough to match a single person. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **channel-mentions**: A space separated list of #channel-mentions which the professor teaches, or #ask-the-staff for a member of the administration
		"""
		# search for professor's details
		# TODO: differentiate between mentions in the query and in channel-mentions
		person = self.finder.search_one(
			args, ctx.message.channel_mentions, ctx.channel, ctx.message.mentions
		)
		self.categoriser.categorise_person(person.id, ctx.message.channel_mentions)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
