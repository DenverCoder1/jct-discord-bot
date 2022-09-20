from typing import Optional, Union
import nextcord
import utils.embedder
from nextcord.ext import commands


class FriendlyError(Exception):
	"""
	An error type that will be sent back to the user who triggered it when raised.
	Should be initialised with as helpful error messages as possible, since these will be shown to the user

	Attributes
	----------
	msg: :class:`str`
			The message to display to the user.
	sender: Union[:class:`nextcord.abc.Messageable`, :class:`nextcord.Interaction`]
			An object which can be used to call send (TextChannel or SlashContext).
	member: Optional[:class:`Member`]
			The member who caused the error.
	inner: Optional[:class:`Exception`]
			An exception that caused the error.
	description: Optional[:class:`str`]
			Description for the FriendlyError embed.
	image: Optional[:class:`str`]
			Image for the FriendlyError embed.
	ephemeral: :class:`bool`
			Whether the message is ephemeral, which means message content will only be seen to the author.
	"""

	def __init__(
		self,
		msg: str,
		sender: Union[nextcord.abc.Messageable, nextcord.Interaction[commands.Bot]],
		member: Union[nextcord.Member, nextcord.User, None] = None,
		inner: Optional[BaseException] = None,
		description: Optional[str] = None,
		image: Optional[str] = None,
		ephemeral: bool = False,
	):
		self.sender = sender
		self.member = member
		self.inner = inner
		self.description = description
		self.image = image
		self.ephemeral = ephemeral
		super().__init__(self.__mention() + msg)

	def __mention(self) -> str:
		return f"Sorry {self.member.display_name}, " if self.member else ""

	async def reply(self):
		embed = utils.embedder.embed_error(
			str(self), description=self.description, image=self.image
		)
		if isinstance(self.sender, nextcord.Interaction):
			await self.sender.send(embed=embed, ephemeral=self.ephemeral)
		else:
			await self.sender.send(embed=embed)
