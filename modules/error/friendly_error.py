import discord
import utils.embedder


class FriendlyError(Exception):
	"""
	An error type that will be sent back to the user who triggered it when raised.
	Should be initialised with as helpful error messages as possible, since these will be shown to the user
	"""

	def __init__(
		self,
		msg: str,
		channel: discord.TextChannel,
		member: discord.Member = None,
		inner: Exception = None,
		description: str = None,
	):
		self.channel = channel
		self.member = member
		self.inner = inner
		self.description = description
		super().__init__(self.__mention() + msg)

	def __mention(self) -> str:
		return f"Sorry {self.member.display_name}, " if self.member is not None else ""

	async def reply(self):
		await self.channel.send(
			embed=utils.embedder.embed_error(str(self), description=self.description)
		)
