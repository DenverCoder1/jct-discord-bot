from utils.utils import blockquote
from modules.error.friendly_error import FriendlyError
from discord.ext import commands
from .formatting_tip import Tip


class TipFormatter:
	def __init__(self):
		# maps format name to pair containing preview markdown and escaped markdown
		self.formats = {
			"italics": Tip("*italics*", "\*italics* or \_italics_"),
			"bold": Tip("**bold text**", "\**bold text**"),
			"underline": Tip("__underline__", "\__underline__"),
			"strikethrough": Tip("~~strikethrough~~", "\~~strikethrough~~"),
			"spoiler": Tip("||spoiler|| (click to reveal)", "\||spoiler||"),
			"inline": Tip("`inline code`", "\`inline code`"),
			"codeblock": Tip(
				'```cpp\ncout << "Code Block";\n```',
				'\```cpp\n// replace this with your code\ncout << "Code Block";\n```',
			),
		}
		# alternative ways to request formats (spaces and case is already ignored)
		self.aliases = {
			"italic": "italics",
			"inlinecode": "inline",
			"spoilers": "spoiler",
			"underlines": "underline",
			"code": "codeblock",
			"codeblocks": "codeblock",
			"codesnippet": "codeblock",
			"snippet": "codeblock",
			"strike": "strikethrough",
		}

	def all_markdown_tips(self) -> str:
		"""return a list of all markdown tips"""
		message = "**__Markdown Tips__**\n\n"
		for format in self.formats:
			tip = self.formats[format]
			message += f"{tip.preview}\n"
			message += f"{blockquote(tip.escaped)}\n\n"
		return message

	def individual_info(self, ctx: commands.Context, format: str) -> str:
		"""return info for given format"""
		format = self.__normalize(ctx, format)
		tip = self.formats[format]
		header_text = self.__header(format, tip)
		how_to = blockquote(tip.escaped)
		footer_text = self.__footer(format)
		return f"{header_text}\n\n{how_to}\n\n{footer_text}"

	def __normalize(self, ctx: commands.Context, format: str) -> str:
		"""normalize format to match format keys"""
		# convert to lowercase
		lower_format = format.lower()
		# check if inputted format is recognized
		if lower_format in self.formats:
			return lower_format
		# check for aliases
		elif lower_format in self.aliases:
			return self.aliases[lower_format]
		# format is not recognized
		else:
			raise FriendlyError(
				f"'{format}' is not a recognized format.", ctx.channel, ctx.author
			)

	def __header(self, format: str, tip: Tip) -> str:
		if format == "codeblock":
			return (
				"Did you know you can format your code with a monospace font and syntax"
				" highlighting on Discord?"
			)
		else:
			return f"Did you know you can format your message with {tip.preview}?"

	def __footer(self, format: str) -> str:
		if format == "codeblock":
			return (
				"Copy the snippet above into a message and insert your code in the"
				" middle. You can also change the syntax highlighting language by"
				" replacing `cpp` with another language, for example, `js`, `py`, or"
				" `java`."
			)
		else:
			return "Copy the snippet into a message replacing the text with your own."