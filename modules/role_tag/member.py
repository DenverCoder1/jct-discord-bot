from .role import Role
import discord
from typing import List


class Member:
	"""
	Represents a member and their role tags
	"""

	def __init__(
		self, member: discord.Member, name_sep: str = " | ", tag_sep: str = " "
	):
		self.inner_member = member
		self.name_sep = name_sep
		self.tag_sep = tag_sep
		self.base_name = (
			member.nick.rsplit(name_sep, 1)[0].strip()
			if member.nick is not None
			else member.display_name
		)

	def current_tags(self) -> List[str]:
		"""Gets a list of tags the user currently has in their nickname"""
		if self.inner_member.nick is None:
			return []
		split = self.inner_member.nick.split(self.base_name + self.name_sep)
		if len(split) > 1:
			return split[1].split(self.tag_sep)
		return []

	def tags(self) -> List[str]:
		"""Gets a list of tags the user should have based on their roles"""
		roles = sorted(
			self.inner_member.roles, key=lambda role: role.position, reverse=True
		)
		_roles = [Role(role) for role in roles]
		return [role.tag.strip() for role in _roles if role.tag]

	def tags_str(self) -> str:
		"""Gets a string to append to a member's name to represent their tags"""
		tags = self.tags()
		return (self.name_sep + self.tag_sep.join(tags)) if tags else ""

	async def apply_tags(self):
		"""Applies all the tags of the member's roles to their nickname"""
		new_nick = self.base_name + self.tags_str()
		await self.inner_member.edit(nick=new_nick)