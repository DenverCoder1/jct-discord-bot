from typing import Iterable
from utils.embedder import build_embed
from database.person import Person
import discord


def gen_embed(person: Person):
	return build_embed(
		title=person.name,
		description=(
			f"{person.linked_emails}\n{person.categories}".strip()
			or "No info found."
		),
		colour=discord.Colour.teal(),
	)


def gen_embeds(people: Iterable[Person]):
	return [gen_embed(person) for person in people]