from database import sql_fetcher
from utils.mention import decode_channel_mention
import config


def get_channel_full_name(channel_id: int) -> str:
	"""Searches the database for the course name given the channel id"""
	query = sql_fetcher.fetch(
		"modules", "calendar", "queries", "search_category_name.sql"
	)
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(query, {"channel": channel_id})
			row = cursor.fetchone()
	if row is not None:
		# return full matched category name from database
		return row[0]
	else:
		# return the channel name instead
		ch = config.guild().get_channel(channel_id)
		return ch.name if ch else f"<#{channel_id}>"


def map_channel_mention(word: str) -> str:
	"""given a word in a string, return the channel name
	if it is a channel mention, otherwise return the original word"""
	channel_id = decode_channel_mention(word)
	# convert mention to full name if word is a mention
	if channel_id:
		return get_channel_full_name(channel_id)
	# not a channel mention
	return word


def replace_channel_mentions(text: str) -> str:
	return " ".join(
		map_channel_mention(word)
		for word in text.replace("<", " <").replace(">", "> ").split()
	)
