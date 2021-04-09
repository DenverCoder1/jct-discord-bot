from . import html_parser
from discord.ext import commands
from utils.utils import one, wait_for_reaction
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from .calendar import Calendar
from .event import Event
from typing import Iterable, Dict, Optional, Sequence
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

	def __format_paragraph(self, text: str, limit: int = 200) -> str:
		"""Trims a string of text to approximately `limit` characters,
		but preserves links using markdown if they get cut off"""
		text = text.replace("<br>", "\n")
		# if limit is in the middle of a link, let the whole link through (shortened reasonably)
		for match in html_parser.match_md_links(text):
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

	def __footer_text(self, page_num: Optional[int] = None) -> str:
		"""Return text about timezone to display at end of embeds with dates"""
		page_num_text = f"Page {page_num} | " if page_num is not None else ""
		timezone_text = f"Times are shown for {self.timezone}"
		return page_num_text + timezone_text
