from database import sql
from utils.mention import decode_channel_mention
import config


async def get_channel_full_name(channel_id: int) -> str:
	"""Searches the database for the course name given the channel id

	Args:
		channel_id (int): The ID of the channel to search for.

	Returns:
		str: The name of the course linked to the channel, or the name of the channel if it doesn't belong to a course.
	"""
	name = await sql.select.value("categories", "name", channel=channel_id)
	if name:
		return name
	channel = config.guild().get_channel(channel_id)
	return channel.name if channel else f"<#{channel_id}>"


async def map_channel_mention(word: str) -> str:
	"""given a word in a string, return the channel name
	if it is a channel mention, otherwise return the original word"""
	channel_id = decode_channel_mention(word)
	# convert mention to full name if word is a mention
	if channel_id:
		return await get_channel_full_name(channel_id)
	# not a channel mention
	return word


async def replace_channel_mentions(text: str) -> str:
	return " ".join(
		[
			await map_channel_mention(word)
			for word in text.replace("<", " <").replace(">", "> ").split()
		]
	)
