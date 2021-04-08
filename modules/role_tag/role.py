import discord


class Role:
	"""
	Represents a role which may contain tags in the name
	"""

	def __init__(self, role: discord.Role, sep: str = "|") -> None:
		self.inner_role = role
		self.sep = sep
		split = self.inner_role.name.rsplit(sep, 1)
		self.tag = split[1] if len(split) == 2 else None