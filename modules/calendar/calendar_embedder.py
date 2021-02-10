from datetime import datetime
from typing import Iterable, Dict
import discord
from utils.utils import parse_date


class CalendarEmbedder:
	def __init__(self):
		self.timezone = "Asia/Jerusalem"

	def embed_event_list(
		self,
		title: str,
		events: Iterable[dict],
		description: str = "",
		colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Generates an embed with event summaries, links, and dates for each event in the given list"""
		embed = discord.Embed(title=title, colour=colour)
		# set initial description if available
		embed.description = "" if description == "" else f"{description}\n\n"
		if not events:
			embed.description += "No events found"
		else:
			# add events to embed
			event_details = map(self.__get_formatted_event_details, events)
			embed.description += "\n".join(event_details)
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
		self,
		title: str,
		event: Dict[str, str],
		colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Embed an event with the summary, link, and dates"""
		embed = discord.Embed(title=title, colour=colour)
		# add overview of event to the embed
		embed.description = self.__get_formatted_event_details(event)
		embed.set_footer(text=self.__get_footer_text())
		return embed

	def embed_success(
		self,
		title: str,
		description: str = None,
		colour: discord.Colour = discord.Colour.green(),
	) -> discord.Embed:
		"""Embed a success message and an optional description"""
		embed = discord.Embed(title=title, colour=colour)
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
		start_date = parse_date(start, tz=self.timezone)
		end_date = parse_date(end, tz=self.timezone)
		# all day event
		if "date" in event["start"]:
			return f"{self.__format_date(start_date, all_day=True)} - All day"
		# start and end time
		return (
			f"{self.__format_date(start_date)} -"
			f" {self.__format_date(end_date, base=start_date)}"
		)

	def __format_date(
		self, date: datetime, base: datetime = None, all_day: bool = False
	) -> str:
		"""Convert dates to a specified format"""
		# if the date is same as the base, only return the time
		if base and date.strftime("%d %b") == base.strftime("%d %b"):
			# return the time (format: '3:45 AM')
			return date.strftime("%I:%M %p").lstrip("0")
		# if the date is in the current year
		if date.year == base.year:
			# if all day, return the date without the time
			if all_day:
				# return the date, month (format: 'Sun 1 Feb')
				return date.strftime("%a %d %b").replace(" 0", " ")
			# return the date, month, and time (format: 'Sun 1 Feb 3:45 AM')
			return date.strftime("%a %d %b %I:%M %p").replace(" 0", " ")
		# the date is in a different year
		else:
			# if all day, return the date without the time
			if all_day:
				# return the date, month, year (format: 'Sun 1 Feb 2020')
				return date.strftime("%a %d %b %Y").replace(" 0", " ")
			# return the date, month, year, and time (format: 'Sun 1 Feb 2020 3:45 AM')
			return date.strftime("%a %d %b %Y %I:%M %p").replace(" 0", " ")

	def __get_footer_text(self):
		"""Return text about timezone to display at end of embeds with dates"""
		return f"Times are shown for {self.timezone}"
