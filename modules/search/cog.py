# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 16:15:06 2021

@author: pinny
"""

from discord.ext import commands
from googlesearch import search
from modules.search.search_functions import *

class Search(commands.Cog):
	def __init__(self, bot, last_paragraph=[None]):
		self.bot = bot
		self.last_paragraph = last_paragraph

	@commands.command(name="search")
	async def search(self, ctx):
		"""search command to message Google links and a small summary (when feesible) for a given prompt"""
		searched_string = ctx.message.content[9:]

		if searched_string.lower() == ":continue": # extra parameter to continue the last search
			await next_paragraph(ctx, self.last_paragraph)
			return

		async with ctx.typing():
			links = search(searched_string, num_results=1)
			wiki = get_wiki(searched_string)
			wiki_intro = get_wiki_intro(wiki, self.last_paragraph)

		await send_message(ctx, searched_string, wiki_intro, links)


# setup functions for bot
def setup(bot):
	bot.add_cog(Search(bot))