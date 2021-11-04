from typing import Optional
from bs4 import BeautifulSoup
from utils.utils import remove_tabs

def format_message(query: str, url: str, result_string: Optional[str] = None) -> str:
	"""formats the message"""
	return remove_tabs(
		f"Search results for: {query}"
		+ (f"\n> {result_string}" if result_string else "")
		+ f"\n~ {url}"
	)

def get_list_string(list_tag) -> str:
	"""Formats an HTML list tag into a string"""
	list_item_tags = list_tag.find_all("li")

	result = ""

	for num, item in enumerate(list_item_tags):
		result = result + f"{num + 1}) " + item.get_text() + " "
	return result