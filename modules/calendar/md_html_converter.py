import re

import lxml
from lxml.html import HtmlElement
from markdown import markdown
from markdownify import markdownify


def md_to_html(md: str) -> str:
    return markdown(md)


def html_to_md(html: str) -> str:
    root = lxml.html.fromstring(html)
    __format_links(root)
    return markdownify(lxml.html.tostring(root, encoding="unicode", method="html")).strip()


def __format_links(root: HtmlElement) -> None:
    """
    Set title attributes of <a> tags to match href if not yet defined.
    Shorten links.
    Modifies existing tree under root.
    """
    for a in root.iter(tag="a"):
        __default_link_title(a)
        __shorten_link(a)


def __default_link_title(a: HtmlElement) -> None:
    """Sets title attributes of <a> tags to match href if title attribute is not set."""
    if not a.get("title"):
        a.set("title", a.get("href"))


# Group 1: The domain + up to 16 more characters
# Group 2: All leftover characters, else empty string
__SHORT_LINK_REGEX = re.compile("https?://(?:www.)?([^/?#]*.{,16})(.*)")


def __shorten_link(a: HtmlElement) -> None:
    """If a link's label is the same as its URL, the label is shortened to the domain plus 16 characters and an elipsis where appropriate."""
    if a.text == a.get("href"):
        match = __SHORT_LINK_REGEX.match(a.text or "")
        assert match is not None
        a.text = match.group(1) + "..." if match.group(2) else ""
