from typing import Iterable
from modules.email_registry.person import Person
from utils import utils
import discord

# TODO: deprecated
def gen_embed(people: Iterable[Person]) -> discord.Embed:
	embed = discord.Embed(colour=discord.Colour.teal())

	for person in people:
		embed.add_field(
			name=person.name,
			value=(
				utils.blockquote(f"{person.linked_emails()}\n{person.categories}")
				or utils.blockquote("No info found.")
			),
			inline=False,
		)

	return embed


def _gen_embed(person: Person):
	return discord.Embed(
		title=person.name,
		description=f"{person.linked_emails()}\n{person.categories}".strip()
		or "No info found.",
		colour=discord.Colour.teal(),
	)


def gen_embeds(people: Iterable[Person]):
	return [_gen_embed(person) for person in people]