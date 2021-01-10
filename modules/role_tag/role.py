import discord


class Role:
	"""
	Represents a role which may contain tags in the name
	"""

	def __init__(self, full_name: str, sep: str = "|") -> None:
		self.full_name = full_name
		self.sep = sep
		split = full_name.rsplit(sep, 1)
		self.short_name = split[0]
		self.tag = split[1] if len(split) == 2 else None

	def has_tag(self):
		return self.tag is not None

	async def give_tag(self, member: discord.Member):
		"""
		TODO: documentation
		"""
		if self.tag is None:
			return

		# if member already has tag, return

		new_nick = (
			member.display_name
			+ (
				(" " + self.sep + " ")
				if member.nick is None or self.sep not in member.nick
				else " "
			)
			+ self.tag
		)
		await member.edit(nick=new_nick)