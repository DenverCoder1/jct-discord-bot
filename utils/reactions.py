import asyncio
import discord
from typing import Collection, Optional, Sequence
from discord.errors import NotFound
from discord.ext import commands
from modules.error.friendly_error import FriendlyError
from utils.utils import one


async def wait_for_reaction(
	bot: commands.Bot,
	message: discord.Message,
	emoji_list: Sequence[str],
	allowed_users: Optional[Collection[discord.Member]] = None,
	timeout: int = 60,
) -> int:
	"""Add reactions to message and wait for user to react with one.
	Returns the index of the selected emoji (integer in range 0 to len(emoji_list) - 1)

	Arguments:
	<bot>: str - the bot user
	<message>: str - the message to apply reactions to
	<emoji_list>: Iterable[str] - list of emojis as strings to add as reactions
	[allowed_users]: Iterable[discord.Member] - if specified, only reactions from these users are accepted
	[timeout]: int - number of seconds to wait before timing out
	"""

	def validate_reaction(reaction: discord.Reaction, user: discord.Member) -> bool:
		"""Validates that:
		- The reaction is on the message currently being checked
		- The emoji is one of the emojis on the list
		- The reaction is not a reaction by the bot
		- The user who reacted is one of the allowed users
		"""
		return (
			reaction.message.id == message.id
			and str(reaction.emoji) in emoji_list
			and user != bot.user
			and (allowed_users is None or user in allowed_users)
		)

	# add reactions to the message
	for emoji in emoji_list:
		await message.add_reaction(emoji)

	try:
		# wait for reaction (returns reaction and user)
		reaction, _ = await bot.wait_for(
			"reaction_add", check=validate_reaction, timeout=timeout
		)
	except asyncio.TimeoutError as error:
		try:
			# clear reactions
			await message.clear_reactions()
		except NotFound:
			# do nothing if message was deleted
			pass
		# raise timeout error as friendly error
		raise FriendlyError(
			f"You did not react within {timeout} seconds",
			message.channel,
			one(allowed_users) if allowed_users and len(allowed_users) == 1 else None,
			error,
		)
	else:
		# clear reactions
		await message.clear_reactions()
		# return the index of the emoji selection
		return emoji_list.index(str(reaction.emoji))