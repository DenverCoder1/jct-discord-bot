from datetime import datetime
from typing import Iterable, Dict
import discord
import dateparser


class CalendarEmbedder:
	def __init__(self):
		self.default_time_zone = "Asia/Jerusalem"

	def embed_event_list(
		self, title: str, events: Iterable[dict], query: str = ""
	) -> discord.Embed:
		"""Generates an embed with event summaries, links, and dates for each event in the given list"""
		embed = discord.Embed(title=title, colour=discord.Colour.green())
		# set initial description with search query if available
		embed.description = "" if query == "" else f'Showing results for "{query}"\n\n'
		if not events:
			embed.description += "No events found"
		else:
			# add events to embed
			event_details = map(self.__get_formatted_event_details, events)
			embed.description += "\n".join(event_details)
		embed.set_footer(text=self.__get_footer_text())
		return embed

	def embed_link(self, title: str, links: Dict[str, str]) -> discord.Embed:
		"""Embed a list of links given a mapping of link text to urls"""
		embed = discord.Embed(title=title, colour=discord.Colour.green())
		# add links to embed
		description = (f"\n**[{text}]({url})**" for text, url in links.items())
		embed.description = "\n".join(description)
		return embed

	def embed_event(self, title: str, event: Dict[str, str]) -> discord.Embed:
		"""Embed an event with the summary, link, and dates"""
		embed = discord.Embed(title=title, colour=discord.Colour.green())
		# add overview of event to the embed
		embed.description = self.__get_formatted_event_details(event)
		embed.set_footer(text=self.__get_footer_text())
		return embed

	def embed_success(self, title: str, description: str = None) -> discord.Embed:
		"""Embed a success message and an optional description"""
		embed = discord.Embed(title=title, colour=discord.Colour.green())
		if description:
			embed.description = description
		return embed

	def __get_formatted_event_details(self, event: Dict[str, str]) -> str:
		"""Format event as a markdown linked summary and the dates below"""
		return (
			f"**[{event.get('summary')}]({event.get('htmlLink')})**\n"
			f"{self.__get_formatted_date_range(event)}\n"
		)

	def __get_formatted_date_range(self, event: Dict[str, str]) -> str:
		"""Extract dates from event and convert to readable format"""
		start = event["start"].get("dateTime", event["start"].get("date"))
		end = event["end"].get("dateTime", event["end"].get("date"))
		start_date = self.__parse_date(start)
		end_date = self.__parse_date(end)
		return (
			f"{self.__format_date(start_date)} -"
			f" {self.__format_date(end_date, base=start_date)}"
		)

	def __parse_date(self, date_str: str) -> datetime:
		"""Returns datetime object with default timezone for given date string"""
		return dateparser.parse(
			date_str, settings={"TO_TIMEZONE": self.default_time_zone}
		)

	def __format_date(self, date: datetime, base: datetime = None) -> str:
		"""Convert dates to a specified format"""
		# if the date is same as base, only return the time
		if base and date.strftime("%d %b") == base.strftime("%d %b"):
			# return the time (format: '3:45 AM')
			return date.strftime("%I:%M %p").lstrip("0")
		# date is in the current year
		if date.year == datetime.now().year:
			# return the date, month, and time (format: 'Sun 1 Feb 3:45 AM')
			return date.strftime("%a %d %b %I:%M %p").replace(" 0", " ")
		# date is in a different year
		else:
			# return the date, month, year, and time (format: 'Sun 1 Feb 2020 3:45 AM')
			return date.strftime("%a %d %b %Y %I:%M %p").replace(" 0", " ")

	def __get_footer_text(self):
		"""Return text about timezone to display at end of embeds with dates"""
		return f"Times are shown for {self.default_time_zone}"
