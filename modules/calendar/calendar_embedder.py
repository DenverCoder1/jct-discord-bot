import re
from discord.ext import commands
from utils.utils import wait_for_reaction
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from .calendar import Calendar
from .event import Event
from typing import Iterable, Dict
from functools import reduce
import discord


class CalendarEmbedder:
	def __init__(self, bot: commands.Bot):
		self.timezone = "Asia/Jerusalem"
		self.max_length = 2048
		self.bot = bot

	async def embed_event_pages(
		self,
		ctx: SlashContext,
		events: Iterable[Event],
		full_query: str,
		results_per_page: int,
		calendar: Calendar,
	) -> None:
		# set start index
		page_num = 1 if len(events) > results_per_page else None
		while True:
			try:
				start = (page_num - 1) * results_per_page if page_num else 0
				# create embed
				embed = self.embed_event_list(
					title=f"📅 Upcoming Events for {calendar.name}",
					events=events[start : start + results_per_page],
					description=f'Showing results for "{full_query}"'
					if full_query
					else "",
					page_num=page_num,
				)
				sender = ctx.send if ctx.message is None else ctx.message.edit
				await sender(embed=embed)
				# if only 1 page, break out of loop
				if page_num is None:
					break
				# default emoji
				next_emoji = "⏬"
				# increment page number
				page_num += 1
				# change emoji and reset page if no more events
				if start + results_per_page >= len(events):
					next_emoji = "⤴️"
					page_num = 1
				# wait for author to respond to go to next page
				await wait_for_reaction(
					bot=self.bot,
					message=ctx.message,
					emoji_list=[next_emoji],
					allowed_users=[ctx.author],
				)
			# time window exceeded
			except FriendlyError:
				break

	def embed_event_list(
		self,
		title: str,
		events: Iterable[Event],
		description: str = "",
		colour: discord.Colour = discord.Colour.blue(),
		enumeration: Iterable[str] = [],
		page_num: int = None,
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
				event_description = "\n"
				# add enumeration emoji if available
				if i < len(enumeration):
					event_description += f"{enumeration[i]} "
				# add the event details
				event_description += self.__format_event(event)
				# make sure embed doesn't exceed max size
				if len(embed.description + event_description) > self.max_length:
					break
				# add event to embed
				embed.description += event_description
		embed.set_footer(text=self.__footer_text(page_num=page_num))
		return embed

	def embed_link(
		self,
		title: str,
		links: Dict[str, str],
		colour: discord.Colour = discord.Colour.dark_blue(),
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

	def __footer_text(self, page_num: int = None) -> str:
		"""Return text about timezone to display at end of embeds with dates"""
		page_num_text = f"Page {page_num} | " if page_num is not None else ""
		timezone_text = f"Times are shown for {self.timezone}"
		return page_num_text + timezone_text
