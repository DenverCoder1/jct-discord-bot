import discord
from typing import Optional, Union
from discord.embeds import EmptyEmbed, _EmptyEmbed
from utils import utils


def embed_success(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	image: Optional[str] = None,
) -> discord.Embed:
	"""Embed a success message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.green(), image)


def embed_warning(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	image: Optional[str] = None,
) -> discord.Embed:
	"""Embed a warning message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.gold(), image)


def embed_error(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	image: Optional[str] = None,
) -> discord.Embed:
	"""Embed an error message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, discord.Colour.red(), image)


def build_embed(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Union[str, _EmptyEmbed] = EmptyEmbed,
	colour: discord.Colour = discord.Colour.blurple(),
	image: Optional[str] = None,
) -> discord.Embed:
	"""Embed a message and an optional description, footer, and url"""
	# create the embed
	embed = discord.Embed(title=utils.trim(title, 256), url=url, colour=colour)
	if description:
		embed.description = utils.trim(description, 2048)
	if footer:
		embed.set_footer(text=utils.trim(footer, 2048))
	if image:
		embed.set_image(url=image)
	return embed
