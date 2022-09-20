from typing import Optional
from utils.utils import blockquote


class Tip:
	def __init__(
		self,
		name: str,
		preview: str,
		escaped: str,
		header: Optional[str] = None,
		footer: Optional[str] = None,
	):
		self.name = name
		self.preview = preview
		self.escaped = escaped
		self.header = header or self.__header()
		self.footer = footer or self.__footer()

	def short_message(self) -> str:
		return f"{self.preview}\n{blockquote(self.escaped)}"

	def long_message(self) -> str:
		return f"{self.header}\n\n{blockquote(self.escaped)}\n\n{self.footer}"

	def __header(self) -> str:
		return f"Did you know you can format your message with {self.preview}?"

	def __footer(self) -> str:
		return "Copy the snippet into a message replacing the text with your own."
