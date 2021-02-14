import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Slash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.slash.get_cog_commands(self)

	@cog_ext.cog_slash(name="embed")
	async def _embed(self, ctx: SlashContext):
		embed = discord.Embed(title="message")
		await ctx.send(embeds=[embed])


def setup(bot):
	bot.add_cog(Slash(bot))
