from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet

from utils.utils import remove_tabs


def remove_citations(wiki_paragraph):
    """Removes citations from a string from a wiki"""
    while True:
        start_of_brackets = wiki_paragraph.find("[")
        end_of_brackets = wiki_paragraph.find("]")

        if start_of_brackets != -1 and end_of_brackets != -1:
            wiki_paragraph = (
                wiki_paragraph[:start_of_brackets] + wiki_paragraph[end_of_brackets + 1 :]
            )
        else:
            break
    return wiki_paragraph


def get_wiki(url: str) -> ResultSet:
    """Does basic setup and formatting of a given wiki page. Returns the plain text of the article."""
    wiki_info = requests.get(url)
    page = BeautifulSoup(wiki_info.content, "html.parser")
    body = page.find(id="bodyContent")
    assert isinstance(body, Tag)
    wiki_html = body.find_all("p")
    return wiki_html


def get_wiki_intro(wiki_link: str) -> str:
    """Finds the into to the wiki from the text of the wiki"""
    wiki = get_wiki(wiki_link)

    # iterate through the paragraphs of the wiki
    for par_obj in wiki:
        paragraph = par_obj.get_text()

        # can remove bad articles by checking the length of the current paragraph
        if len(paragraph) < 150:
            continue

        return f"\n> {remove_citations(paragraph).strip()}\n~ Wikipedia (<{wiki_link}>).\n"

    return ""


def format_message(query: str, url: str, wiki_string: Optional[str] = None) -> str:
    """Formats the message"""
    return remove_tabs(f"Search results for: {query}\n{wiki_string or ''}\n{url}")
