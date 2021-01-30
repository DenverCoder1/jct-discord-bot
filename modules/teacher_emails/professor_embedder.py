from typing import Iterable
from modules.teacher_emails.professor import Professor
from utils import utils
import discord


class ProfessorEmbedder:
	def gen_embed(self, profs: Iterable[Professor]) -> discord.Embed:
		embed = discord.Embed(colour=discord.Colour.green())

		for prof in profs:
			if prof.emails:
				embed.add_field(
					name=prof.name,
					value=utils.blockquote(f"{prof.linked_emails()}\n{prof.subjects}"),
					inline=False,
				)

		return embed