from modules.role_tag.role import Role
from modules.role_tag.member import Member
from discord.ext import commands
import discord


class RoleTagsCog(commands.Cog, name="Role Tags"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before: discord.Member, after: discord.Member):
		before = Member(before)
		after = Member(after)
		if after.current_tags() != after.tags():
			await after.apply_tags()
			print(
				"Renamed",
				before.inner_member.display_name,
				"to",
				after.inner_member.display_name,
			)

	@commands.Cog.listener()
	async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
		before = Role(before)
		after = Role(after)
		if before.tag != after.tag:
			print(before.inner_role.name, "changed to", after.inner_role.name)
			for member in after.inner_role.members:
				await Member(member).apply_tags()


def setup(bot: commands.Bot):
	bot.add_cog(RoleTagsCog(bot))