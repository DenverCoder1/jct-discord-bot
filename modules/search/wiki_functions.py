from bs4.element import ResultSet
import requests
from bs4 import BeautifulSoup

def remove_citations(wiki_paragraph):
	"""removes citations from a string from a wiki"""
	while True:
		start_of_brackets = wiki_paragraph.find("[")
		end_of_brackets = wiki_paragraph.find("]")

		if start_of_brackets != -1 and end_of_brackets != -1:
			wiki_paragraph = (
				wiki_paragraph[:start_of_brackets]
				+ wiki_paragraph[end_of_brackets + 1 :]
			)
		else:
			break
	return wiki_paragraph


def get_wiki(url: str) -> ResultSet:
	"""Does basic setup and formatting of a given wiki page. Returns the plain text of the article."""
	wiki_info = requests.get(url)
	page = BeautifulSoup(wiki_info.content, "html.parser")
	wiki_html = page.find(id="bodyContent").find_all("p")
	return wiki_html


def get_wiki_intro(wiki_link: str) -> str:
	"""finds the into to the wiki from the text of the wiki"""
	wiki = get_wiki(wiki_link)

	# iterate through the paragraphs of the wiki
	for par_obj in wiki:
		paragraph = par_obj.get_text()

		# can remove bad articles by checking the length of the current paragraph
		if len(paragraph) < 150:
			continue

		return remove_citations(paragraph).strip()

	return ""