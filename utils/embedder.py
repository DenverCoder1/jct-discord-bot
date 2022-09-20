import nextcord
from typing import Optional, Union
from utils import utils

MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_EMBED_FIELD_TITLE_LENGTH = 256
MAX_EMBED_FIELD_FOOTER_LENGTH = 2048


def embed_success(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Optional[str] = None,
	image: Optional[str] = None,
) -> nextcord.Embed:
	"""Embed a success message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, nextcord.Colour.green(), image)


def embed_warning(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Optional[str] = None,
	image: Optional[str] = None,
) -> nextcord.Embed:
	"""Embed a warning message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, nextcord.Colour.gold(), image)


def embed_error(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Optional[str] = None,
	image: Optional[str] = None,
) -> nextcord.Embed:
	"""Embed an error message and an optional description, footer, and url"""
	return build_embed(title, description, footer, url, nextcord.Colour.red(), image)


def build_embed(
	title: str,
	description: Optional[str] = None,
	footer: Optional[str] = None,
	url: Optional[str] = None,
	colour: nextcord.Colour = nextcord.Colour.blurple(),
	image: Optional[str] = None,
) -> nextcord.Embed:
	"""Embed a message and an optional description, footer, and url"""
	# create the embed
	embed = nextcord.Embed(
		title=utils.trim(title, MAX_EMBED_FIELD_TITLE_LENGTH), url=url, colour=colour
	)
	if description:
		embed.description = utils.trim(description, MAX_EMBED_DESCRIPTION_LENGTH)
	if footer:
		embed.set_footer(text=utils.trim(footer, MAX_EMBED_FIELD_FOOTER_LENGTH))
	if image:
		embed.set_image(url=image)
	return embed
