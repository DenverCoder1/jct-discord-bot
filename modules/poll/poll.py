import discord
from typing import Dict, List
from modules.error.friendly_error import FriendlyError

# TODO
# if user forgot time, don't pop
# allow JCT bot to vote multiple times
# give option to allow others to nominate poll options


class Poll:
	def __init__(self, msg: discord.Message):
		self.msg = msg
		self.title = self.__extract_title()
		self.duration = self.__extract_duration()
		self.options = self.__extract_options()
		self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
		self.embed = self.__create_embed()
		self.voters: Dict[discord.Member, discord.Reaction] = {}
		self.fraudsters: List[discord.Member] = []  # attempted to vote twice

	def __extract_title(self) -> str:
		try:
			return self.msg.content.split("\n")[1].strip()
		except IndexError:
			raise FriendlyError("Poll command needs a title.", self.msg.channel)

	def __extract_duration(self) -> int:
		str_duration = self.msg.content.split("\n")[2].strip()
		units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
		unit = str_duration[-1]
		try:
			return int(str_duration[:-1]) * units[unit]
		except (ValueError, KeyError):
			return 3600

	# should probably make an options class
	def __extract_options(self) -> List[str]:
		options = [option.strip() for option in self.msg.content.split("\n")[3:]]
		if len(options) < 2:
			raise FriendlyError("Please provide at least two options", self.msg.channel)
		return options

	def __create_embed(self):
		embed = discord.Embed(title=self.title)
		embed.set_author(
			name=self.msg.author.display_name, icon_url=str(self.msg.author.avatar_url)
		)
		for i in range(len(self.options)):
			embed.add_field(name=self.emojis[i], value=self.options[i], inline=True)
		return embed

	async def vote(self, reaction: discord.Reaction, member: discord.Member):
		# print(member.display_name + "attempting to vote")
		if member in self.voters:
			# print(member.display_name + "already voted")
			self.fraudsters.append(member)
			await reaction.remove(member)
			# print(member.display_name + "already voted - done")
		else:
			self.voters[member] = reaction
			# print(member.display_name + "successfully voted")

	async def unvote(self, reaction: discord.Reaction, member: discord.Member):
		# print(member.display_name + "successfully unvoted")
		if member not in self.fraudsters:
			self.voters.pop(member)
		self.fraudsters.pop(0)
