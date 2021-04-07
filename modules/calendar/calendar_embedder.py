import re
from discord.ext import commands
from utils.utils import one, wait_for_reaction
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from .calendar import Calendar
from .event import Event
from typing import Iterable, Dict, Optional, Sequence
from functools import reduce
import discord


class CalendarEmbedder:
	def __init__(self, bot: commands.Bot, timezone: str):
		self.bot = bot
		self.timezone = timezone
		# maximum length of embed description
		self.max_length = 2048
		# emoji list for enumerating events
		self.number_emoji = (
			"0️⃣",
			"1️⃣",
			"2️⃣",
			"3️⃣",
			"4️⃣",
			"5️⃣",
			"6️⃣",
			"7️⃣",
			"8️⃣",
			"9️⃣",
		)
		# symbols that can't be inside URL
		URL_INVALID = r"\s()\[\],!<>|\"{}"
		# regex for parsing url
		self.URL_REGEX = re.compile(
			fr"https?://(?:www\.)?([^/{URL_INVALID}]*/?[^{URL_INVALID}]{{1,3}})([^{URL_INVALID}]*)"
		)
		# regex to match URL and URL title attribute inside parentheses
		self.FULL_URLS_REGEX = re.compile(
			fr'\(({self.URL_REGEX.pattern} "{self.URL_REGEX.pattern}")\)'
		)
		# regex to match HTML opening and closing tags
		self.HTML_TAG_REGEX = re.compile(r"</?.*?>")

	async def embed_event_pages(
		self,
		ctx: SlashContext,
		events: Sequence[Event],
		query: str,
		results_per_page: int,
		calendar: Calendar,
	):
		"""Embed page of events and wait for reactions to continue to new pages"""
		# set start index
		page_num = 1 if len(events) > results_per_page else None
		while True:
			try:
				# first event to display
				start = (page_num - 1) * results_per_page if page_num else 0
				# create embed
				embed = self.embed_event_list(
					title=f"📅 Upcoming Events for {calendar.name}",
					events=events[start : start + results_per_page],
					description=f'Showing results for "{query}"' if query else "",
					page_num=page_num,
				)
				sender = ctx.send if ctx.message is None else ctx.message.edit
				await sender(embed=embed)
				# if only one page, break out of loop
				if not page_num:
					break
				# set emoji and page based on if no more events
				if start + results_per_page < len(events):
					next_emoji = "⏬"
					page_num += 1
				else:
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

	async def get_event_choice(
		self, ctx: SlashContext, events: Sequence[Event], query: str, action: str,
	) -> Event:
		"""
		If there are no events, throws an error.
		If there are multiple events, embed list of events and wait for reaction to select an event.
		If there is one event, return it.
		"""
		# no events found
		if not events:
			raise FriendlyError(f'No events were found for "{query}".', ctx, ctx.author)
		# if only 1 event found, get the event at index 0
		if len(events) == 1:
			return one(events)
		# multiple events found
		embed = self.embed_event_list(
			title=f"⚠ Multiple events were found.",
			events=events,
			description=(
				f"Please specify which event you would like to {action}."
				f'\n\nShowing results for "{query}"'
			),
			colour=discord.Colour.gold(),
			enumeration=self.number_emoji,
		)
		await ctx.send(embed=embed)
		# ask user to pick an event with emojis
		selection_index = await wait_for_reaction(
			bot=self.bot,
			message=ctx.message,
			emoji_list=self.number_emoji[: len(events)],
			allowed_users=[ctx.author],
		)
		# get the event selected by the user
		return events[selection_index]

	def embed_event_list(
		self,
		title: str,
		events: Iterable[Event],
		description: str = "",
		colour: discord.Colour = discord.Colour.blue(),
		enumeration: Sequence[str] = (),
		page_num: Optional[int] = None,
	) -> discord.Embed:
		"""Generates an embed with event summaries, links, and dates for each event in the given list

		Arguments:

		:param title: :class:`str` the title to display at the top
		:param events: :class:`Iterable[Event]` the events to display
		:param description: :class:`Optional[str]` the description to embed below the title
		:param colour: :class:`Optional[discord.Colour]` the embed colour
		:param enumeration: :class:`Optional[Iterable[str]]` list of emojis to display alongside events (for reaction choices)
		"""
		embed = discord.Embed(title=title, colour=colour)
		# set initial description if available
		embed.description = "" if description == "" else f"{description}\n"
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

	def embed_links(
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

	def __shorten_links(self, text: str) -> str:
		"""remove the protocol and most of path from URLs in text"""
		# Replace links with shortened forms in markdown linking to full url and including title attributes
		return self.URL_REGEX.sub(
			lambda m: f'[{m.group(1)}{"..." if m.group(2) else ""}]({m.group(0)} "{m.group(0)}")',
			text,
		)

	def __remove_html_tags(self, text: str) -> str:
		"""remove html tags from text"""
		# replace <br> with newline
		text = text.replace("<br>", "\n")
		# remove html tags
		return self.HTML_TAG_REGEX.sub("", text)

	def __format_paragraph(self, text: str, max: int = 100) -> str:
		"""Trims a string of text to a maximum number of characters,
		but preserves links using markdown if they get cut off"""
		# check for server emoji tags and increase max by the sum of the characters in the emoji tags
		emoji_list = re.findall(r"<:[\w-]+:\d+>", text[:max])
		max += reduce(lambda acc, next: acc + len(next) - 1, emoji_list, 0)
		# remove html tags
		html_tags_removed = self.__remove_html_tags(text)
		# replace links with shortened versions in markdown
		shortened_links = self.__shorten_links(html_tags_removed)
		# replace full urls and titles with placeholders to not include them when trimming
		trimmed = self.FULL_URLS_REGEX.sub("({})", shortened_links)
		# shift 'max' to the index of the next word in the text or the end of the text if none
		match = re.search(r"(\b\s|$)", trimmed[max:])
		assert match is not None
		max += match.start()
		# trim the text normally
		trimmed = trimmed[:max].strip() + "..." if len(trimmed) > max else trimmed
		# get full urls to replace placeholders
		full_urls = self.FULL_URLS_REGEX.findall(shortened_links)
		# put the full urls back into the text
		for full_url in full_urls:
			trimmed = re.sub(r"\({}\)", f"({full_url[0]})", trimmed, count=1)
		return trimmed

	def __format_event(self, event: Event) -> str:
		"""Format event as a markdown linked summary and the dates below"""
		info = f"**[{event.title}]({event.link})**\n"
		info += f"{event.relative_date_range_str()}\n"
		if event.description:
			info += f"{self.__format_paragraph(event.description)}\n"
		if event.location:
			info += f":round_pushpin: {self.__format_paragraph(event.location)}\n"
		return info

	def __footer_text(self, page_num: Optional[int] = None) -> str:
		"""Return text about timezone to display at end of embeds with dates"""
		page_num_text = f"Page {page_num} | " if page_num is not None else ""
		timezone_text = f"Times are shown for {self.timezone}"
		return page_num_text + timezone_text
