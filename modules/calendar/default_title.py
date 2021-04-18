from markdown import Markdown
from markdown.postprocessors import Postprocessor
import xml.etree.ElementTree as ET
from markdown.extensions import Extension


class DefaultTitleProcessor(Postprocessor):
	def run(self, html: str):
		"""
		Set title attributes of <a> tags if not yet defined.
		"""
		root = ET.fromstring(html)
		for child in root.iter(tag="a"):
			if not child.get("title", None):
				url = child.get("href", None)
				if url:
					child.set("title", url)
		return ET.tostring(root, "unicode", "html")


class DefaultTitle(Extension):
	"""
	Markdown extension to set link titles to the URL, if not specified.
	"""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def extendMarkdown(self, md: Markdown):
		md.registerExtension(self)
		md.postprocessors.register(DefaultTitleProcessor(md), "Default Title", 1000)
