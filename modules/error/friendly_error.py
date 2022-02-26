from typing import Any, Callable, Optional, Union
import nextcord
import utils.embedder
from mypy_extensions import DefaultNamedArg


class FriendlyError(Exception):
	"""
	An error type that will be sent back to the user who triggered it when raised.
	Should be initialised with as helpful error messages as possible, since these will be shown to the user

	Attributes
	----------
	msg: :class:`str`
			The message to display to the user.
	send_func: :class:`Callable`
			A function with a similar signature to any `send` function which will be used to send the message.
	member: Optional[:class:`Member`]
			The member who caused the error.
	inner: Optional[:class:`Exception`]
			An exception that caused the error.
	description: Optional[:class:`str`]
			Description for the FriendlyError embed.
	image: Optional[:class:`str`]
			Image for the FriendlyError embed.
	ephemeral: :class:`bool`
			Whether the message is hidden, which means message content will only be seen to the author.
	"""

	def __init__(
		self,
		msg: str,
		send_func: Callable[[DefaultNamedArg(nextcord.Embed, "embed")], Any,],
		member: Union[nextcord.Member, nextcord.User, None] = None,
		inner: Optional[BaseException] = None,
		description: Optional[str] = None,
		image: Optional[str] = None,
		ephemeral: bool = False,
	):
		self.send = send_func
		self.member = member
		self.inner = inner
		self.description = description
		self.image = image
		self.ephemeral = ephemeral
		super().__init__(self.__mention() + msg)

	def __mention(self) -> str:
		return f"Sorry {self.member.display_name}, " if self.member else ""

	async def reply(self):
		await self.send(
			embed=utils.embedder.embed_error(
				str(self), description=self.description, image=self.image
			),
			**{"ephemeral": self.ephemeral} if self.ephemeral else {},
		)
