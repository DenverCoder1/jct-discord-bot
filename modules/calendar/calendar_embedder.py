from __future__ import annotations
import re
from typing import Dict, Generator, Optional, Sequence
from discord.ext import commands
from utils.utils import one, wait_for_reaction
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from .calendar import Calendar
from .event import Event
from more_itertools import peekable
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

	async def embed_event_pages(
		self,
		ctx: SlashContext,
		events_list: Sequence[Event],
		query: str,
		results_per_page: int,
		calendar: Calendar,
	):
		"""Embed page of events and wait for reactions to continue to new pages"""
		# peekable generator for events
		events = peekable(events_list)
		# set start index
		page_num = 1 if len(events_list) > results_per_page else None
		while True:
			try:
				# create embed
				embed = self.embed_event_list(
					title=f"📅 Upcoming Events for {calendar.name}",
					events=events,
					calendar=calendar,
					description=f'Showing results for "{query}"' if query else "",
					page_num=page_num,
					max_results=results_per_page,
				)
				sender = ctx.send if ctx.message is None else ctx.message.edit
				await sender(embed=embed)
				# if only one page, break out of loop
				if not page_num:
					break
				# set emoji and page based on whether there are more events
				if events:
					next_emoji = "⏬"
					page_num += 1
				else:
					next_emoji = "⤴️"
					page_num = 1
					# reset the peekable generator
					events = peekable(events_list)
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
		self,
		ctx: SlashContext,
		events_list: Sequence[Event],
		calendar: Calendar,
		query: str,
		action: str,
	) -> Event:
		"""
		If there are no events, throws an error.
		If there are multiple events, embed list of events and wait for reaction to select an event.
		If there is one event, return it.
		"""
		# no events found
		if not events_list:
			raise FriendlyError(f'No events were found for "{query}".', ctx, ctx.author)
		# if only 1 event found, get the event at index 0
		if len(events_list) == 1:
			return one(events_list)
		# create a peekable iterable of events
		events = peekable(events_list)
		# multiple events found
		embed = self.embed_event_list(
			title=f"⚠ Multiple events were found.",
			events=events,
			calendar=calendar,
			description=(
				f"Please specify which event you would like to {action}."
				f'\n\nShowing results for "{query}"'
			),
			colour=discord.Colour.gold(),
			enumeration=self.number_emoji,
		)
		await ctx.send(embed=embed)
		# get the number of events that were displayed
		next_event = events.peek(None)
		num_events = events_list.index(next_event) if next_event else len(events_list)
		# ask user to pick an event with emojis
		selection_index = await wait_for_reaction(
			bot=self.bot,
			message=ctx.message,
			emoji_list=self.number_emoji[:num_events],
			allowed_users=[ctx.author],
		)
		# get the event selected by the user
		return events_list[selection_index]

	def embed_event_list(
		self,
		title: str,
		events: peekable[Event],
		calendar: Calendar,
		description: str = "",
		colour: discord.Colour = discord.Colour.blue(),
		enumeration: Sequence[str] = (),
		page_num: Optional[int] = None,
		max_results: int = 10,
	) -> discord.Embed:
		"""Generates an embed with event summaries, links, and dates for each event in the given list

		Arguments:

		:param title: :class:`str` the title to display at the top
		:param events: :class:`peekable[Event]` the events to display
		:param calendar: :class:`Calendar` the calendar the events are from
		:param description: :class:`Optional[str]` the description to embed below the title
		:param colour: :class:`Optional[discord.Colour]` the embed colour
		:param enumeration: :class:`Optional[Iterable[str]]` list of emojis to display alongside events (for reaction choices)
		:param page_num: :class:`Optional[int]` page number to display in the footer
		:param max_results: :class:`int` maximum results to display in the list
		"""
		embed = discord.Embed(title=title, colour=colour)
		# get calendar links
		links = self.__calendar_links(calendar)
		# limit max results to the number of emojis in the enumeration
		max_results = min(max_results, len(enumeration)) if enumeration else max_results
		# set initial description if available
		embed.description = f"{description}\n" if description else ""
		# check if events peekable is empty
		embed.description += "No events found.\n" if not events else ""
		# create iterator for enumeration
		enumerator = iter(enumeration)
		# add events to embed
		for _ in range(max_results):
			event = events.peek(None)
			# if event is None, no more events
			if not event:
				break
			# get event details and add enumeration emoji if available
			event_details = f"\n{next(enumerator, '')} {self.__format_event(event)}"
			# make sure embed doesn't exceed max length
			if len(embed.description + event_details + links) > self.max_length:
				break
			# add event to embed
			embed.description += event_details
			# consume event
			next(events)
		# add links for viewing and editing on Google Calendar
		embed.description += links
		# add page number and timezone info
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
		self,
		title: str,
		event: Event,
		calendar: Calendar,
		colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Embed an event with the summary, link, and dates"""
		embed = discord.Embed(title=title, colour=colour)
		# add overview of event to the embed
		embed.description = self.__format_event(event)
		# add links for viewing and editing on Google Calendar
		embed.description += self.__calendar_links(calendar)
		# add timezone info
		embed.set_footer(text=self.__footer_text())
		return embed

	def __format_paragraph(self, text: str, limit: int = 100) -> str:
		"""Trims a string of text to approximately `limit` displayed characters,
		but preserves links using markdown if they get cut off"""
		text = text.replace("<br>", "\n")
		# if limit is in the middle of a link, let the whole link through (shortened reasonably)
		for match in self.__match_md_links(text):
			# increase limit by the number of hidden characters
			limit += len(f"[]({match.group(2)})")
			# if match extends beyond the limit, move limit to the end of the match
			if match.end() > limit:
				limit = match.end() if match.start() < limit else limit
				break
		return text[:limit].strip() + "..." if len(text) > limit else text.strip()

	def __format_event(self, event: Event) -> str:
		"""Format event as a markdown linked summary and the dates below"""
		info = f"**[{event.title}]({event.link})**\n"
		info += f"{event.relative_date_range_str()}\n"
		if event.description:
			info += f"{self.__format_paragraph(event.description)}\n"
		if event.location:
			info += f":round_pushpin: {self.__format_paragraph(event.location)}\n"
		return info

	def __calendar_links(self, calendar: Calendar) -> str:
		"""Return text with links to view or edit the Google Calendar"""
		return (
			f"\n[👀 View events]({calendar.view_url(self.timezone)}) | [✏️ Edit"
			f" with Google]({calendar.add_url()}) (use `/calendar grant` for access)"
		)

	def __footer_text(self, page_num: Optional[int] = None) -> str:
		"""Return text about timezone to display at end of embeds with dates"""
		page_num_text = f"Page {page_num} | " if page_num is not None else ""
		timezone_text = f"Times are shown for {self.timezone}"
		return page_num_text + timezone_text

	__MD_LINK_REGEX = re.compile(
		# Group 1: The label
		# Group 2: The full URL including any title text
		# Group 3: The full URL without the title text
		r"\[(.*?[^\\])\]\(((https?:\/\/\S+).*?)\)"
	)

	@classmethod
	def __match_md_links(cls, text: str) -> Generator[re.Match, None, None]:
		start = 0
		match = cls.__MD_LINK_REGEX.search(text)
		while match:
			yield match
			start = match.end()
			match = cls.__MD_LINK_REGEX.search(text, pos=start)