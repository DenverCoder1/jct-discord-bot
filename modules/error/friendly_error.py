from typing import Optional, Union
import discord
from discord_slash.context import SlashContext
import utils.embedder


class FriendlyError(Exception):
	"""
	An error type that will be sent back to the user who triggered it when raised.
	Should be initialised with as helpful error messages as possible, since these will be shown to the user

	Attributes
	----------
	   msg: :class:`str`
	       The message to display to the user.
	   sender: :class:`Union[discord.TextChannel, SlashContext]`
	       An object which can be used to call send (TextChannel or SlashContext).
	   member: Optional[:class:`Member`]
	       The member who caused the error.
	   inner: Optional[:class:`Exception`]
	       An exception that caused the error.
	   description: Optional[:class:`str`]
	       Description for the FriendlyError embed.
	"""

	def __init__(
		self,
		msg: str,
		sender: Union[discord.abc.Messageable, SlashContext],
		member: Union[discord.Member, discord.User, None] = None,
		inner: Optional[BaseException] = None,
		description: Optional[str] = None,
	):
		self.sender = sender
		self.member = member
		self.inner = inner
		self.description = description
		super().__init__(self.__mention() + msg)

	def __mention(self) -> str:
		return f"Sorry {self.member.display_name}, " if self.member else ""

	async def reply(self):
		if isinstance(self.sender, SlashContext) and self.sender.message is not None:
			sender = self.sender.channel  # slash command has already been answered
		else:
			sender = self.sender
		await sender.send(
			embed=utils.embedder.embed_error(str(self), description=self.description)
		)
