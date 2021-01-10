from modules.role_tag.member import Member
from discord.ext import commands
import discord


class RoleTagsCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before: discord.Member, after: discord.Member):
		# - check which roles the user has
		if before.roles != after.roles:
			print("Renaming", before.nick + "...")
			await Member(after).apply_tags()
			print("Renamed", before.nick, "to", after.nick)


def setup(bot):
	bot.add_cog(RoleTagsCog(bot))