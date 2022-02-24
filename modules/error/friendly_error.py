from typing import Optional, Union
import nextcord
import utils.embedder


class FriendlyError(Exception):
	"""
	An error type that will be sent back to the user who triggered it when raised.
	Should be initialised with as helpful error messages as possible, since these will be shown to the user

	Attributes
	----------
	msg: :class:`str`
			The message to display to the user.
	sender: :class:`Union[nextcord.TextChannel, SlashContext]`
			An object which can be used to call send (TextChannel or SlashContext).
	member: Optional[:class:`Member`]
			The member who caused the error.
	inner: Optional[:class:`Exception`]
			An exception that caused the error.
	description: Optional[:class:`str`]
			Description for the FriendlyError embed.
	image: Optional[:class:`str`]
			Image for the FriendlyError embed.
	hidden: :class:`bool`
			Whether the message is hidden, which means message content will only be seen to the author.
	"""

	def __init__(
		self,
		msg: str,
		messageable: nextcord.abc.Messageable,
		member: Union[nextcord.Member, nextcord.User, None] = None,
		inner: Optional[BaseException] = None,
		description: Optional[str] = None,
		image: Optional[str] = None,
		hidden: bool = False,
	):
		self.sender = messageable
		self.member = member
		self.inner = inner
		self.description = description
		self.image = image
		self.hidden = hidden
		super().__init__(self.__mention() + msg)

	def __mention(self) -> str:
		return f"Sorry {self.member.display_name}, " if self.member else ""

	async def reply(self):
		if isinstance(self.sender, SlashContext) and self.sender.message is not None:
			sender = self.sender.channel  # slash command has already been answered
		else:
			sender = self.sender
		await sender.send(
			embed=utils.embedder.embed_error(
				str(self), description=self.description, image=self.image
			),
			hidden=self.hidden,
		)
