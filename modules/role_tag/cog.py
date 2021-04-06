from modules.role_tag.role import Role
from modules.role_tag.member import Member
from discord.ext import commands
import discord


class RoleTagsCog(commands.Cog, name="Role Tags"):
	"""Changes nicknames to include tags represented by the user's roles"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before: discord.Member, after: discord.Member):
		_before = Member(before)
		_after = Member(after)
		if _after.current_tags() != _after.tags():
			await _after.apply_tags()
			print(
				"Renamed",
				_before.inner_member.display_name,
				"to",
				_after.inner_member.display_name,
			)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
		_before = Role(before)
		_after = Role(after)
		if _before.tag != _after.tag:
			print(_before.inner_role.name, "changed to", _after.inner_role.name)
			for member in _after.inner_role.members:
				await Member(member).apply_tags()


def setup(bot: commands.Bot):
	bot.add_cog(RoleTagsCog(bot))