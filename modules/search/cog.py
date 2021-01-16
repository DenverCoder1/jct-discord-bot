# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 16:15:06 2021

@author: pinny
"""

from discord.ext import commands
from googlesearch import search
import modules.search.search_functions as sf
import config


class Search(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.last_paragraph = {}

	@commands.command(name="search")
	async def search(self, ctx):
		"""search command to message Google links and a small summary (when feasible) for a given prompt"""
		searched_string = ctx.message.content[len(config.prefix) + 6 :].strip()

		channel_id = ctx.channel.id
		if channel_id not in self.last_paragraph:
			self.last_paragraph[channel_id] = None

		if (
			searched_string.lower() == ":continue"
		):  # extra parameter to continue the last search
			await sf.next_paragraph(ctx, self.last_paragraph)
			return

		async with ctx.typing():
			links = search(searched_string, num_results=1)
			wiki, wiki_link = sf.get_wiki(searched_string)
			wiki_intro = sf.get_wiki_intro(wiki, wiki_link, self.last_paragraph, channel_id)

		await sf.send_message(ctx, searched_string, wiki_intro, links)


# setup functions for bot
def setup(bot):
	bot.add_cog(Search(bot))