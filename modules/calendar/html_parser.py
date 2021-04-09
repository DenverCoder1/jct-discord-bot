import re
from typing import Generator

__MD_LINK_REGEX = re.compile(
	# Group 1: The label
	# Group 2: The full URL
	r"\[(.*?[^\\])\]\((https?:\/\/.*?)\)"
)
__HTML_LINK_REGEX = re.compile(
	# Group 2|5: The full URL
	# Group 3|6: A truncated URL, if the label was the same as the URL
	# Group 4: The label if it was not the same as the URL
	r"(?:<a\s+(?:[^>]*?\s+)?href=(['\"])(.*?)\1.*?>(?:(?=\2)https?://(.*?(?=[/<#?])[^<?#]{0,10}).*?|(.*?))<\/a>|(https?://([\w.@:]+[^\s()\[\],!<>|\"'{}]{0,9})[^\s()\[\],!<>|\"'{}]*))"
)


def md_links_to_html(text: str) -> str:
	return __MD_LINK_REGEX.sub(r"<a href='\2'>\1</a>", text)


def html_links_to_md(text: str) -> str:
	def repl(match):
		"""parses link regex as a shortened markdown link with full link as title attribute"""
		partial_link = match.group(3) or match.group(6)
		label = match.group(4)
		full_link = match.group(2) or match.group(5)
		trimmed = partial_link in full_link and not full_link.endswith(partial_link)
		label = label or (partial_link + ("..." if trimmed else ""))
		return f'[{label}]({full_link} "{full_link}")'

	return __HTML_LINK_REGEX.sub(repl, text)


def match_md_links(text: str) -> Generator[re.Match, None, None]:
	start = 0
	match = __MD_LINK_REGEX.search(text)
	while match:
		yield match
		start = match.end()
		match = __MD_LINK_REGEX.search(text, pos=start)
