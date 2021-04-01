import discord


def embed_success(
	title: str,
	description: str = None,
	colour: discord.Colour = discord.Colour.green(),
) -> discord.Embed:
	"""Embed a success message and an optional description"""
	return __embed(title, description, colour)


def embed_warning(
	title: str, description: str = None, colour: discord.Colour = discord.Colour.gold(),
) -> discord.Embed:
	"""Embed a warning message and an optional description"""
	return __embed(title, description, colour)


def embed_error(
	title: str, description: str = None, colour: discord.Colour = discord.Colour.red(),
) -> discord.Embed:
	"""Embed an error message and an optional description"""
	return __embed(title, description, colour)


def __embed(title: str, description: str, colour: discord.Colour) -> discord.Embed:
	"""Embed a message and an optional description"""
	embed = discord.Embed(title=title, colour=colour)
	if description:
		embed.description = description
	return embed