from utils.utils import one
from utils.mention import extract_channel_mentions
import discord
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from modules.email_registry.categoriser import Categoriser
from modules.email_registry import person_embedder
from modules.email_registry.person_finder import PersonFinder
from modules.email_registry.email_adder import EmailAdder
from modules.email_registry.person_adder import PersonAdder
from modules.error.friendly_error import FriendlyError
from discord.ext import commands
import config


class EmailRegistryCog(commands.Cog, name="Email Registry"):
	"""Update and retrieve faculty emails from the registry"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = PersonFinder(config.conn, config.sql_fetcher)
		self.email_adder = EmailAdder(config.conn, config.sql_fetcher)
		self.person_adder = PersonAdder(config.conn, config.sql_fetcher)
		self.categoriser = Categoriser(config.conn, config.sql_fetcher)

	@cog_ext.cog_subcommand(
		base="email",
		name="of",
		description="Get the email address of the person you search for.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="name",
				description="First name, last name, or both. (eg. moti)",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="channel",
				description="Mention a course the professor teaches. (eg. #automata)",
				option_type=SlashCommandOptionType.CHANNEL,
				required=False,
			),
		],
	)
	async def get_email(
		self,
		ctx: SlashContext,
		name: str = None,
		course_channel: discord.TextChannel = None,
	):
		await ctx.defer()  # let discord know the response may take more than 3 seconds
		people = self.finder.search(name, course_channel or ctx.channel)
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

	@cog_ext.cog_subcommand(
		base="email",
		name="add",
		description="Add the email of a professor with this command.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="email",
				description="The email address you wish to add to the person.",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="name",
				description="First name, last name, or both. (eg. moti)",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="channel",
				description="Mention a course the professor teaches. (eg. #automata)",
				option_type=SlashCommandOptionType.CHANNEL,
				required=False,
			),
		],
	)
	async def add_email(
		self,
		ctx: SlashContext,
		email: str,
		name: str = None,
		channel: discord.TextChannel = None,
	):
		await self.__add_remove_emails(
			name=name,
			channel=channel,
			email=email,
			ctx=ctx,
			func=self.email_adder.add_email,
		)

	@cog_ext.cog_subcommand(
		base="email",
		name="remove",
		description="Remove the email of a professor with this command.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="email",
				description="The email address you wish to remove from its owner.",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
		],
	)
	@commands.has_guild_permissions(manage_roles=True)
	async def remove_email(self, ctx: SlashContext, email: str):
		await self.__add_remove_emails(
			email=email, ctx=ctx, func=self.email_adder.remove_email
		)

	@cog_ext.cog_subcommand(
		base="email",
		subcommand_group="person",
		name="add",
		description="Add a faculty member to the email registry.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="first_name",
				description="The first name of the person you want to add.",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="last_name",
				description="The last name of the person you want to add.",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="channels",
				description="Mention the channels this person is associated with.",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
		],
	)
	@commands.has_guild_permissions(manage_roles=True)
	async def add_person(
		self, ctx: SlashContext, first_name: str, last_name: str, channels: str
	):
		await ctx.defer()
		person_id = self.person_adder.add_person(
			first_name, last_name, extract_channel_mentions(channels), self.categoriser,
		)
		person = one(self.finder.get_people([person_id]))
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

	async def __add_remove_emails(
		self,
		ctx: SlashContext,
		func,
		name: str = None,
		channel: discord.TextChannel = None,
		email: str = None,
	):
		await ctx.defer()
		# search for professor's details
		# if either name or channel are provided, no need to search using email
		person = self.finder.search_one(
			ctx, name, channel, None if (name or channel) is not None else email
		)
		# add/remove the emails to the database
		func(person, email, ctx)
		# update professors set from database
		person = one(self.finder.get_people([person.id]))
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
		person = one(self.finder.get_people([person.id]))
		await ctx.send(embed=person_embedder.gen_embed(person))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
