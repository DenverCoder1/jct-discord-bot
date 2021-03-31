from typing import Iterable
from modules.email_registry.person import Person
from utils import utils
import discord


class PersonEmbedder:
	def gen_embed(self, people: Iterable[Person]) -> discord.Embed:
		embed = discord.Embed(colour=discord.Colour.green())

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