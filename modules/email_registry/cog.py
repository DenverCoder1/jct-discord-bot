from utils.embedder import embed_success
from modules.email_registry import person_remover
from discord.channel import TextChannel
import config
import discord
from database.person import Person
from typing import Any, Callable, Coroutine, Iterable, Optional
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from . import person_embedder
from . import categoriser
from . import person_finder
from . import email_adder
from . import person_adder
from ..error.friendly_error import FriendlyError
from utils.mention import extract_channel_mentions


class EmailRegistryCog(commands.Cog):
	"""Update and retrieve faculty emails from the registry"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

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
		people = await person_finder.search(
			name,
			channel
			or (ctx.channel if isinstance(ctx.channel, discord.TextChannel) else None),
		)
		people = {person for person in people if person.emails}
		if not people:
			if name or channel:
				raise FriendlyError(
					"The email you are looking for aught to be here... But it isn't."
					" Perhaps the archives are incomplete.",
					ctx,
				)
			raise FriendlyError(
				"Please specify the professor's name or channel of the email you are"
				" looking for.",
				ctx,
				image="https://media.discordapp.net/attachments/798518399842910228/849023621460131872/EmailSlashCommand.gif",
			)
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
		person = await person_finder.search_one(ctx, name, channel)
		# add the emails to the database
		person = await email_adder.add_email(person, email, ctx)
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
		person = await person_finder.search_one(ctx, email=email)
		# add/remove the emails to the database
		person = await email_adder.remove_email(person, email, ctx)
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
		self, ctx: SlashContext, first_name: str, last_name: str, channels: str = ""
	):
		await ctx.defer()
		person = await person_adder.add_person(
			first_name, last_name, extract_channel_mentions(channels), ctx
		)
		await ctx.send(embed=person_embedder.gen_embed(person))

	@cog_ext.cog_subcommand(
		base="email",
		subcommand_group="person",
		name="remove",
		description="Remove a faculty member from the email registry.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="name",
				description="The name of the person you want to remove.",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="channel",
				description="A channel this person is associated with.",
				option_type=SlashCommandOptionType.CHANNEL,
				required=False,
			),
			create_option(
				name="email",
				description="The email address of the person you want to remove.",
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
		],
	)
	@commands.has_guild_permissions(manage_roles=True)
	async def remove_person(
		self,
		ctx: SlashContext,
		name: Optional[str] = None,
		channel: Optional[TextChannel] = None,
		email: Optional[str] = None,
	):
		await ctx.defer()
		person = await person_remover.remove_person(ctx, name, channel, email)
		await ctx.send(
			embed=embed_success(f"Successfully removed {person.name} from the system.")
		)

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
			ctx, name_or_email, channel_mentions, categoriser.categorise_person
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
			ctx, name_or_email, channel_mentions, categoriser.decategorise_person
		)

	async def __link_unlink(
		self,
		ctx: SlashContext,
		name_or_email: str,
		channel_mentions: str,
		func: Callable[[SlashContext, int, Iterable[str]], Coroutine[Any, Any, Person]],
	):
		await ctx.defer()
		person = await person_finder.search_one(
			ctx, name=name_or_email, email=name_or_email
		)
		person = await func(ctx, person.id, extract_channel_mentions(channel_mentions))
		await ctx.send(embed=person_embedder.gen_embed(person))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
