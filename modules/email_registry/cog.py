from utils.embedder import embed_success
from modules.email_registry import person_remover
from nextcord.channel import TextChannel
import config
import nextcord
from database.person import Person
from typing import Any, Callable, Coroutine, Iterable, Optional
from nextcord.ext import commands
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

	@nextcord.slash_command(name="email", guild_ids=[config.guild_id])
	async def email(self, interaction: nextcord.Interaction[commands.Bot]):
		"""This is a base command for the email registr and is not invoked"""
		pass

	@email.subcommand(name="of")
	async def get_email(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		name: Optional[str] = None,
		channel: Optional[nextcord.TextChannel] = None,
	):
		"""Get the email address of the person you search for.
		
		Args:
			name: First name, last name, or both. (eg. moti)
			channel: Mention a course the professor teaches. (eg. #automata)
		"""
		await interaction.response.defer()
		people = await person_finder.search(
			name,
			channel
			or (interaction.channel if isinstance(interaction.channel, nextcord.TextChannel) else None),
		)
		people = {person for person in people if person.emails}
		if not people:
			if name or channel:
				raise FriendlyError(
					"The email you are looking for aught to be here... But it isn't."
					" Perhaps the archives are incomplete.",
					interaction,
					description="🥚 Can i offer you a nice egg in this trying time?",
				)
			raise FriendlyError(
				"Please specify the professor's name or channel of the email you are"
				" looking for.",
				interaction,
				image="https://media.discordapp.net/attachments/798518399842910228/849023621460131872/EmailSlashCommand.gif",
			)
		embeds = person_embedder.gen_embeds(people)
		await interaction.send(embeds=embeds)

	@email.subcommand(name="add")
	async def add_email(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		email: str,
		name: Optional[str] = None,
		channel: Optional[nextcord.TextChannel] = None,
	):
		"""Add the email of a professor with this command.

		Args:
			email: The email address you wish to add to the person.
			name: First name, last name, or both. (eg. moti)
			channel: Mention a course the professor teaches. (eg. #automata)
		"""
		await interaction.response.defer()
		# search for professor's details
		person = await person_finder.search_one(interaction, name, channel)
		# add the emails to the database
		person = await email_adder.add_email(person, email, interaction)
		await interaction.send(embed=person_embedder.gen_embed(person))

	@email.subcommand(name="remove")
	@commands.has_guild_permissions(manage_roles=True)
	async def remove_email(self, interaction: nextcord.Interaction[commands.Bot], email: str):
		"""Remove the email of a professor with this command.

		Args:
			email: The email address you wish to remove from its owner.
		"""
		await interaction.response.defer()
		# search for professor's details
		person = await person_finder.search_one(interaction, email=email)
		# add/remove the emails to the database
		person = await email_adder.remove_email(person, email)
		await interaction.send(embed=person_embedder.gen_embed(person))

	@email.subcommand(name="person")
	async def add_person(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		first_name: str,
		last_name: str,
		email: Optional[str] = None,
		channels: str = "",
	):
		"""Add a faculty member to the email registry.

		Args:
			first_name: The first name of the person you want to add.
			last_name: The last name of the person you want to add.
			email: The email address of the person you want to add.
			channels: Mention the channels this person is associated with.
		"""
		await interaction.response.defer()
		person = await person_adder.add_person(
			first_name, last_name, extract_channel_mentions(channels), interaction
		)
		if email is not None:
			person = await email_adder.add_email(person, email, interaction)
		await interaction.send(embed=person_embedder.gen_embed(person))

	@email.subcommand(name="remove")
	@commands.has_guild_permissions(manage_roles=True)
	async def remove_person(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		name: Optional[str] = None,
		channel: Optional[TextChannel] = None,
		email: Optional[str] = None,
	):
		"""Remove a faculty member from the email registry.
		
		Args:
			name: The name of the person you want to remove.
			channel: A channel this person is associated with.
			email: The email address of the person you want to remove.
		"""

		await interaction.response.defer()
		person = await person_remover.remove_person(interaction, name, channel, email)
		await interaction.send(
			embed=embed_success(f"Successfully removed {person.name} from the system.")
		)

	@email.subcommand(name="link")
	@commands.has_guild_permissions(manage_roles=True)
	async def link_person_to_category(
		self, interaction: nextcord.Interaction[commands.Bot], name_or_email: str, channel_mentions: str
	):
		"""Link a person to a category (for example a professor to a course they teach).
		
		Args:
			name_or_email: First name, last name, or both, (eg. moti). Alternatively, you may use the person's email.
			channel_mentions: Mention one or more course channels the professor teaches. (eg. #automata #computability)
		"""

		await self.__link_unlink(
			interaction, name_or_email, channel_mentions, categoriser.categorise_person
		)

	@email.subcommand(name="unlink")
	@commands.has_guild_permissions(manage_roles=True)
	async def unlink_person_from_category(
		self, interaction: nextcord.Interaction[commands.Bot], name_or_email: str, channel_mentions: str
	):
		"""Unlink a person from a category (for example a professor from a course they no longer teach).

		Args:
			name_or_email: First name, last name, or both, (eg. moti). Alternatively, you may use the person's email.
			channel_mentions: Mention the course channels to unlink from the specified person. (eg. #automata #tcp-ip)
		"""

		await self.__link_unlink(
			interaction, name_or_email, channel_mentions, categoriser.decategorise_person
		)

	async def __link_unlink(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		name_or_email: str,
		channel_mentions: str,
		func: Callable[[nextcord.Interaction, int, Iterable[str]], Coroutine[Any, Any, Person]],
	):
		await interaction.response.defer()
		person = await person_finder.search_one(
			interaction, name=name_or_email, email=name_or_email
		)
		person = await func(interaction, person.id, extract_channel_mentions(channel_mentions))
		await interaction.send(embed=person_embedder.gen_embed(person))


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(EmailRegistryCog(bot))
