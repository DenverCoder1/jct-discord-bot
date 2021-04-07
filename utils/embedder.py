import discord
from typing import Optional


def embed_success(
	title: str,
	description: Optional[str] = None,
	colour: discord.Colour = discord.Colour.green(),
) -> discord.Embed:
	"""Embed a success message and an optional description"""
	return __embed(title, description, colour)


def embed_warning(
	title: str,
	description: Optional[str] = None,
	colour: discord.Colour = discord.Colour.gold(),
) -> discord.Embed:
	"""Embed a warning message and an optional description"""
	return __embed(title, description, colour)


def embed_error(
	title: str,
	description: Optional[str] = None,
	colour: discord.Colour = discord.Colour.red(),
) -> discord.Embed:
	"""Embed an error message and an optional description"""
	return __embed(title, description, colour)


def __embed(
	title: str, description: Optional[str], colour: discord.Colour
) -> discord.Embed:
	"""Embed a message and an optional description"""
	embed = discord.Embed(title=title, colour=colour)
	if description:
		embed.description = description
	return embed