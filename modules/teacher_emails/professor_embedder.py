from typing import Iterable

from discord import colour
from modules.teacher_emails.professor import Professor
import discord


class ProfessorEmbedder:
	def gen_embed(self, profs: Iterable[Professor]) -> discord.Embed:
		embed = discord.Embed(colour=discord.Colour.green())

		for prof in profs:
			embed.add_field(
				name=prof.name,
				value=f"> {prof.linked_emails()}\n> {prof.subjects}",
				inline=False,
			)

		return embed