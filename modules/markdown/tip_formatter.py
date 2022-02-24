from nextcord.ext import commands
from .formatting_tip import Tip


formats = {
	"italics": Tip("𝘐𝘵𝘢𝘭𝘪𝘤𝘴", "*italics*", "\*italics* or \_italics_"),
	"bold": Tip("𝗕𝗼𝗹𝗱", "**bold text**", "\**bold text**"),
	"underline": Tip("U͟n͟d͟e͟r͟l͟i͟n͟e͟", "__underline__", "\__underline__"),
	"strikethrough": Tip(
		"S̶t̶r̶i̶k̶e̶t̶h̶r̶o̶u̶g̶h̶", "~~strikethrough~~", "\~~strikethrough~~"
	),
	"spoiler": Tip(
		"███████ (Spoiler)", "||spoiler|| (click to reveal)", "\||spoiler||"
	),
	"inline": Tip("𝙸𝚗𝚕𝚒𝚗𝚎 𝚌𝚘𝚍𝚎", "`inline code`", "\`inline code`"),
	"codeblock": Tip(
		"𝙱𝚕𝚘𝚌𝚔 𝚌𝚘𝚍𝚎",
		'```cpp\ncout << "This is a code block" << endl;\n```',
		"\```cpp\n// replace this with your code\n```",
		footer=(
			"Copy the snippet above into a message and insert your code in the"
			" middle. You can also change the syntax highlighting language by"
			" replacing `cpp` with another language, for example, `js`, `py`,"
			" or `java`."
		),
	),
}


def all_markdown_tips() -> str:
	"""return a list of all markdown tips"""
	message = "**__Markdown Tips__**\n\n"
	for format in formats:
		message += formats[format].short_message() + "\n\n"
	return message


def individual_info(format: str) -> str:
	"""return info for given format"""
	return formats[format].long_message()