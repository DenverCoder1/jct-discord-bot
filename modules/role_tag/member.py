from modules.role_tag.role import Role
import discord
from typing import List


class Member:
	"""
	Represents a member and their role tags
	"""

	def __init__(self, member: discord.Member, sep: str = "|"):
		self.inner_member = member
		self.sep = sep
		self.base_name = (
			member.nick.rsplit(sep, 1)[0].strip()
			if member.nick is not None
			else member.display_name
		)

	def tags(self) -> List[str]:
		roles = sorted(
			self.inner_member.roles, key=lambda role: role.position, reverse=True
		)
		roles = [Role(role) for role in roles]
		return [role.tag.strip() for role in roles if role.has_tag()]

	def tags_str(self) -> str:
		tags = self.tags()
		return " " + self.sep + " " + " ".join(tags) if tags else ""

	async def apply_tags(self):
		"""
		Applies all the tags of the member's roles to their nickname
		"""

		new_nick = self.base_name + self.tags_str()
		await self.inner_member.edit(nick=new_nick)