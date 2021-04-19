import discord
from typing import Optional, Union
from discord.embeds import EmptyEmbed, _EmptyEmbed
from utils import utils


def embed_success(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
) -> discord.Embed:
	"""Embed a success message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.green())


def embed_warning(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
) -> discord.Embed:
	"""Embed a warning message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.gold())


def embed_error(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
) -> discord.Embed:
	"""Embed an error message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.red())


def build_embed(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	colour: discord.Colour = discord.Colour.blurple(),
) -> discord.Embed:
	"""Embed a message and an optional description, footer, and url"""
	# create the embed
	embed = discord.Embed(title=utils.trim(title, 256), url=url, colour=colour)
	if description:
		embed.description = utils.trim(description, 2048)
	if footer:
		embed.set_footer(text=utils.trim(footer, 2048))
	return embed