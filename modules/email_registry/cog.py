import discord
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from modules.email_registry.categoriser import Categoriser
from modules.email_registry import person_embedder
from modules.email_registry.person_finder import PersonFinder
from modules.email_registry.email_adder import EmailAdder
from modules.email_registry.person_adder import PersonAdder
from modules.error.friendly_error import FriendlyError
from modules.role_tag.member import Member
from utils.sql_fetcher import SqlFetcher
from discord.ext import commands
import os
import config


class EmailRegistryCog(commands.Cog, name="Email Registry"):
	"""Update and retrieve faculty emails from the registry"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = PersonFinder(config.conn, config.sql_fetcher)
		self.email_adder = EmailAdder(config.conn, config.sql_fetcher)
		self.person_adder = PersonAdder(config.conn, config.sql_fetcher)
		self.categoriser = Categoriser(config.conn, config.sql_fetcher)

	@cog_ext.cog_slash(
		name="email",
		description="Get the email address of the person you search for",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="name",
				description="Professor's first name, last name, or both. eg moti",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="channel",
				description="Mention a course the professor teaches",
				option_type=SlashCommandOptionType.CHANNEL,
				required=False,
			),
		],
	)
	async def get_email(
		self, ctx: SlashContext, name: str = None, channel: discord.TextChannel = None,
	):
		await ctx.defer()  # let discord know the response may take more than 3 seconds
		people = self.finder.search(name, channel or ctx.channel)
		people = {person for person in people if person.emails}
		if not people:
			raise FriendlyError(
				"The email you are looking for aught to be here... But it isn't."
				" Perhaps the archives are incomplete.",
				ctx,
			)
		else:
			embeds = person_embedder.gen_embeds(people)
			await ctx.send(embeds=embeds)

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
		await self.__add_remove_emails(args, ctx, self.email_adder.add_emails)

	@commands.command(name="removeemail")
	@commands.has_guild_permissions(manage_roles=True)
	async def remove_email(self, ctx: commands.Context, *args):
		"""Remove the email of a professor with this command.

		Usage:
		```
		++removeemail query emails
		```
		Arguments:
		> **query**: A string to identify a person. Must be specific enough to match a single person. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **emails**: One or more of the teacher's email addresses
		"""
		await self.__add_remove_emails(args, ctx, self.email_adder.remove_emails)

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
		person_id = self.person_adder.add_person(
			name, surname, ctx.message.channel_mentions, self.categoriser, member_id
		)
		person = self.finder.get_people([person_id])
		await ctx.send(embed=person_embedder.gen_embed(person))

	@commands.command(name="link")
	@commands.has_guild_permissions(manage_roles=True)
	async def link_person_to_category(self, ctx: commands.Context, *args):
		"""Link a person to a category (for example a professor to a course they teach)

		Usage:
		```
		++link query to channel-mentions
		```
		Arguments:
		> **query**: A string to identify a person. Must be specific enough to match a single person. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **channel-mentions**: A space separated list of #channel-mentions which the professor teaches, or #ask-the-staff for a member of the administration
		"""
		# search for professor's detailschannel-mentions
		await self.__link_unlink(args, ctx, "to", self.categoriser.categorise_person)

	@commands.command(name="unlink")
	@commands.has_guild_permissions(manage_roles=True)
	async def unlink_person_from_category(self, ctx: commands.Context, *args):
		"""Unlink a person from a category (for example a professor from a course they no longer teach)

		Usage:
		```
		++unlink query from channel-mentions
		```
		Arguments:
		> **query**: A string to identify a person. Must be specific enough to match a single person. Can contain their name and/or courses (or their channel mentions) they teach. (e.g. eitan c++)
		> **channel-mentions**: A space separated list of #channel-mentions which the professor teaches, or #ask-the-staff for a member of the administration
		"""
		await self.__link_unlink(
			args, ctx, "from", self.categoriser.decategorise_person
		)

	async def __add_remove_emails(self, args, ctx: commands.Context, func):
		# search for professor's details
		person = self.finder.search_one(args, ctx.channel)
		# add/remove the emails to the database
		func(person, self.email_adder.filter_emails(args))
		# update professors set from database
		person = self.finder.get_people([person.id])
		await ctx.send(embed=person_embedder.gen_embed(person))

	async def __link_unlink(self, args, ctx: commands.Context, sep_word: str, func):
		# search for professor's detailschannel-mentions
		try:
			# index of last occurrence of sep_word in args
			index_sep = len(args) - 1 - args[::-1].index(sep_word)
		except ValueError as e:
			raise FriendlyError(
				f'You must include the word "{sep_word}" in between your query and the'
				" channel mentions",
				ctx.channel,
				ctx.author,
				e,
			)
		person = self.finder.search_one(args[:index_sep], ctx.channel)
		success, error_msg = func(person.id, args[index_sep + 1 :])
		if not success:
			raise FriendlyError(error_msg, ctx.channel, ctx.author)
		person = self.finder.get_people([person.id])
		await ctx.send(embed=person_embedder.gen_embed(person))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
