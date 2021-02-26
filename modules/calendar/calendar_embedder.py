import asyncio
import re
from .event import Event
from typing import Iterable, Dict
from functools import reduce
import discord
from discord.ext import commands
from utils.utils import wait_for_reaction
from modules.error.friendly_error import FriendlyError


class CalendarEmbedder:
	def __init__(self, bot):
		self.bot = bot
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
			event_details = map(self.__get_formatted_event_details, events)
			for i, details in enumerate(event_details):
				# add enumeration emoji if available, otherwise, just the details
				event_description = (
					f"\n{enumeration[i]} {details}"
					if i < len(enumeration)
					else f"\n{details}"
				)
				# make sure embed doesn't exceed max size
				if len(embed.description + event_description) > self.max_length:
					break
				# add event to embed
				embed.description += event_description
		embed.set_footer(text=self.__get_footer_text())
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
		embed.description = self.__get_formatted_event_details(event)
		embed.set_footer(text=self.__get_footer_text())
		return embed

	async def wait_for_selection(
		self,
		ctx: commands.Context,
		message: discord.Message,
		enumeration: Iterable[str],
		num_events: int,
		timeout: int = 60,
	):
		"""Adds reactions to message, waits for selection, clears reactions, and returns selection index"""
		try:
			# get reaction and user
			reaction, _ = await wait_for_reaction(
				bot=self.bot,
				message=message,
				emoji_list=enumeration[:num_events],
				allowed_users=[ctx.author],
				timeout=timeout,
			)
		except asyncio.TimeoutError as error:
			# clear reactions
			await message.clear_reactions()
			# raise timeout error as friendly error
			raise FriendlyError(
				f"You did not react within {timeout} seconds",
				ctx.channel,
				ctx.author,
				error,
			)
		else:
			# clear reactions
			await message.clear_reactions()
			# get emoji selection index
			return enumeration.index(str(reaction.emoji))

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

	def __get_formatted_event_details(self, event: Event) -> str:
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

	def __get_footer_text(self):
		"""Return text about timezone to display at end of embeds with dates"""
		return f"Times are shown for {self.timezone}"
