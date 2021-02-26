import re
from .event import Event
from typing import Iterable, Dict
from functools import reduce
import discord


class CalendarEmbedder:
	def __init__(self):
		self.timezone = "Asia/Jerusalem"
		self.max_length = 2048

	def embed_event_list(
		self,
		title: str,
		events: Iterable[Event],
		description: str = "",
		colour: discord.Colour = discord.Colour.green(),
		enumeration: Iterable[str] = [],
	) -> discord.Embed:
		"""Generates an embed with event summaries, links, and dates for each event in the given list

		Arguments:
		<title> - title to display at the top
		<events> - list of events to embed
		[description] - description to embed below the title
		[colour] - embed colour
		[enumeration] - list of emojis to display alongside events (for reaction choices)
		"""
		embed = discord.Embed(title=title, colour=colour)
		# set initial description if available
		embed.description = "" if description == "" else f"{description}\n\n"
		if not events:
			embed.description += "No events found"
		else:
			# add events to embed
			for i, event in enumerate(events):
				# add enumeration emoji if available, otherwise, just the details
				event_description = (
					f"\n{enumeration[i]} {self.__format_event(event)}"
					if i < len(enumeration)
					else f"\n{self.__format_event(event)}"
				)
				# make sure embed doesn't exceed max size
				if len(embed.description + event_description) > self.max_length:
					break
				# add event to embed
				embed.description += event_description
		embed.set_footer(text=self.__footer_text())
		return embed

	def embed_link(
		self,
		title: str,
		links: Dict[str, str],
		colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Embed a list of links given a mapping of link text to urls"""
		embed = discord.Embed(title=title, colour=colour)
		# add links to embed
		description = (f"\n**[{text}]({url})**" for text, url in links.items())
		embed.description = "\n".join(description)
		return embed

	def embed_event(
		self, title: str, event: Event, colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Embed an event with the summary, link, and dates"""
		embed = discord.Embed(title=title, colour=colour)
		# add overview of event to the embed
		embed.description = self.__format_event(event)
		embed.set_footer(text=self.__footer_text())
		return embed

	def __trim_text_links_preserved(self, text: str, max: int = 30) -> str:
		"""Trims a string of text to a maximum number of characters,
		but preserves links using markdown if they get cut off"""
		# check for server emoji tags and increase max by the sum of the characters in the emoji tags
		emoji_list = re.findall("<:[\w-]+:\d+>", text[:max])
		max += reduce(lambda x, y: x + len(y) - 1, emoji_list, 0)
		# trims the text normally
		trimmed = text[:max].strip() + "..." if len(text) > max else text
		# get the part before and after the text is cut off
		before_match = re.search(r"\S+$", text[:max])
		after_match = re.search(r"^\S+", text[max:])
		if before_match and after_match:
			# get the full word at the cut-off
			before = before_match.group(0)
			after = after_match.group(0)
			full = before + after
			# check if the word that got cut off is a link
			if re.match(r"^https?:\S*$", full):
				# replace link fragment with markdown link
				start = before_match.start()
				trimmed = text[:start] + f'[{before}...]({full} "{full}")'
		return trimmed

	def __format_event(self, event: Event) -> str:
		"""Format event as a markdown linked summary and the dates below"""
		info = f"**[{event.title()}]({event.link()})**\n"
		info += f"{event.date_range_str()}\n"
		if event.description():
			# trim to max 35 chars
			info += f"{self.__trim_text_links_preserved(event.description(), max=35)}\n"
		if event.location():
			# trim to max 30 chars
			info += f":round_pushpin: {self.__trim_text_links_preserved(event.location())}\n"
		return info

	def __footer_text(self):
		"""Return text about timezone to display at end of embeds with dates"""
		return f"Times are shown for {self.timezone}"
