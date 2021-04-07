import config
import discord
from database.person import Person
from typing import Callable, Iterable, Optional
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from . import person_embedder
from .categoriser import Categoriser
from .person_finder import PersonFinder
from .email_adder import EmailAdder
from .person_adder import PersonAdder
from ..error.friendly_error import FriendlyError
from utils.mention import extract_channel_mentions


class EmailRegistryCog(commands.Cog, name="Email Registry"):
	"""Update and retrieve faculty emails from the registry"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.finder = PersonFinder(config.conn)
		self.email_adder = EmailAdder(config.conn)
		self.person_adder = PersonAdder(config.conn)
		self.categoriser = Categoriser(config.conn)

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
		name: Optional[str] = None,
		channel: Optional[discord.TextChannel] = None,
	):
		await ctx.defer()  # let discord know the response may take more than 3 seconds
		people = self.finder.search(
			name,
			channel
			or (ctx.channel if isinstance(ctx.channel, discord.TextChannel) else None),
		)
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
		name: Optional[str] = None,
		channel: Optional[discord.TextChannel] = None,
	):
		await ctx.defer()
		# search for professor's details
		person = self.finder.search_one(ctx, name, channel)
		# add the emails to the database
		person = self.email_adder.add_email(person, email, ctx)
		await ctx.send(embed=person_embedder.gen_embed(person))

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
		await ctx.defer()
		# search for professor's details
		person = self.finder.search_one(ctx, email=email)
		# add/remove the emails to the database
		person = self.email_adder.remove_email(person, email, ctx)
		await ctx.send(embed=person_embedder.gen_embed(person))

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
		person = self.person_adder.add_person(
			first_name,
			last_name,
			extract_channel_mentions(channels),
			self.categoriser,
			ctx,
		)
		await ctx.send(embed=person_embedder.gen_embed(person))

	@cog_ext.cog_subcommand(
		base="email",
		subcommand_group="person",
		name="link",
		description=(
			"Link a person to a category (for example a professor to a course they"
			" teach)."
		),
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="name_or_email",
				description=(
					"First name, last name, or both, (eg. moti). Alternatively, you may"
					" use the person's email."
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="channel_mentions",
				description=(
					"Mention one or more course channels the professor teaches. (eg."
					" #automata #computability)"
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
		],
	)
	@commands.has_guild_permissions(manage_roles=True)
	async def link_person_to_category(
		self, ctx: SlashContext, name_or_email: str, channel_mentions: str
	):
		await self.__link_unlink(
			ctx, name_or_email, channel_mentions, self.categoriser.categorise_person
		)

	@cog_ext.cog_subcommand(
		base="email",
		subcommand_group="person",
		name="unlink",
		description=(
			"Unlink a person from a category (for example a professor from a course"
			" they no longer teach)."
		),
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="name_or_email",
				description=(
					"First name, last name, or both, (eg. moti). Alternatively, you may"
					" use the person's email."
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="channel_mentions",
				description=(
					"Mention the course channels to unlink from the specified person."
					" (eg. #automata #tcp-ip)"
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
		],
	)
	@commands.has_guild_permissions(manage_roles=True)
	async def unlink_person_from_category(
		self, ctx: SlashContext, name_or_email: str, channel_mentions: str
	):
		await self.__link_unlink(
			ctx, name_or_email, channel_mentions, self.categoriser.decategorise_person
		)

	async def __link_unlink(
		self,
		ctx: SlashContext,
		name_or_email: str,
		channel_mentions: str,
		func: Callable[[SlashContext, Person, Iterable[str]], Person],
	):
		await ctx.defer()
		person = self.finder.search_one(ctx, name=name_or_email, email=name_or_email)
		person = func(ctx, person, extract_channel_mentions(channel_mentions))
		await ctx.send(embed=person_embedder.gen_embed(person))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
