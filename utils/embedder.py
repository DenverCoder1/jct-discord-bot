import discord
from typing import Optional, Union
from discord.embeds import EmptyEmbed, _EmptyEmbed
from utils import utils


def embed_success(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	colour: discord.Colour = discord.Colour.green(),
) -> discord.Embed:
	"""Embed a success message and an optional description, footer, and url"""
	return __embed(title, description, footer, url, colour)


def embed_warning(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	colour: discord.Colour = discord.Colour.gold(),
) -> discord.Embed:
	"""Embed a warning message and an optional description, footer, and url"""
	return __embed(title, description, footer, url, colour)


def embed_error(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	colour: discord.Colour = discord.Colour.red(),
) -> discord.Embed:
	"""Embed an error message and an optional description, footer, and url"""
	return __embed(title, description, footer, url, colour)


def __embed(
	title: str,
	description: Optional[str],
	footer: Optional[str],
	url: Union[str, _EmptyEmbed],
	colour: discord.Colour
) -> discord.Embed:
	"""Embed a message and an optional description, footer, and url"""
	# create the embed
	embed = discord.Embed(title=utils.trim(title, 256), url=url, colour=colour)
	if description:
		embed.description = utils.trim(description, 2048)
	if footer:
		embed.set_footer(text=utils.trim(footer, 2048))
	return embed