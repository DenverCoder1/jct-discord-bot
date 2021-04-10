import re
from typing import Generator

__MD_LINK_REGEX = re.compile(
	# Group 1: The label
	# Group 2: The full URL including any title text
	# Group 3: The full URL without the title text
	r"\[(.*?[^\\])\]\(((https?:\/\/\S+).*?)\)"
)

__HTML_LINK_REGEX = re.compile(
	# Group 2|5: The full URL
	# Group 3|6: A truncated URL, if the label was the same as the URL
	# Group 4: The label if it was not the same as the URL
	r"(?:<a\s+(?:[^>]*?\s+)?href=(['\"])(.*?)\1.*?>(?:(?=\2)https?://(.*?(?=[/<#?])[^<?#]{0,10}).*?|(.*?))<\/a>|(https?://([\w.@:]+[^\s()\[\],!<>|\"'{}]{0,9})[^\s()\[\],!<>|\"'{}]*))"
)


def md_links_to_html(text: str) -> str:
	return __MD_LINK_REGEX.sub(r"<a href='\3'>\1</a>", text)


def html_links_to_md(text: str) -> str:
	def link_repl(match):
		"""parses link regex as a shortened markdown link with full link as title attribute"""
		# inner text of the link or None if the text is the link
		inner_text = match.group(4)
		# trimmed version of the link or None if the link has inner text
		partial_link = match.group(3) or match.group(6)
		# full href of the link
		full_link = match.group(2) or match.group(5)
		# check if partial link is a trimmed version of the full link
		trimmed = partial_link and not full_link.endswith(partial_link)
		# set the label for the markdown link
		label = inner_text or partial_link + ("..." if trimmed else "")
		# return markdown link
		return f'[{label}]({full_link} "{full_link}")'

	return __HTML_LINK_REGEX.sub(link_repl, text)


def match_md_links(text: str) -> Generator[re.Match, None, None]:
	start = 0
	match = __MD_LINK_REGEX.search(text)
	while match:
		yield match
		start = match.end()
		match = __MD_LINK_REGEX.search(text, pos=start)
