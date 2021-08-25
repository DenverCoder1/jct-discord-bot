from typing import List, Dict
from discord_slash.utils.manage_components import create_select_option


def create_file_options(files : List[Dict]):
	""" Creates the options for a Discord select menu """
	options = []
	for file in files:
		options.insert(
			0,
			create_select_option(
				file['title'],
				value=file['id'],
				emoji=file['icon'],
			)
		)
		
	return options