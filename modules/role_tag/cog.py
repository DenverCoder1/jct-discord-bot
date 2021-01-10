from modules.role_tag.role import Role
from modules.role_tag.admin_symbol import is_admin, add_symbol, remove_symbol
from discord.ext import commands
import discord


class AdminSymbol(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before: discord.Member, after: discord.Member):
		# - check which roles the user has
		member_roles = [Role(role.name) for role in after.roles]

		# - apply all said tags (if any) to username
		for role in member_roles:
			role.give_tag(after)


def setup(bot):
	bot.add_cog(AdminSymbol(bot))