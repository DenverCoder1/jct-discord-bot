from typing import Iterable, Dict
import discord
import dateparser

class CalendarEmbedder:
	def __init__(self):
		self.default_time_zone = "Asia/Jerusalem"

	def embed_event_list(self, title: str, events: Iterable[dict]) -> discord.Embed:
		"""Generates an embed with a field for each event in the given list"""
		embed = discord.Embed(
			title=title,
			colour=discord.Colour.green()
		)
		if not events:
			embed.description = "No events found"
		else:
			# add events to embed
			event_details = map(self.__get_formatted_event_details, events)
			embed.description = "\n".join(event_details)
		embed.set_footer(text=f"Times are shown for {self.default_time_zone}")
		return embed

	def embed_link(self, title: str, links: Dict[str, str]) -> discord.Embed:
		embed = discord.Embed(
			title=title,
			colour=discord.Colour.green()
		)
		# add links to embed
		description = (f"\n**[{text}]({url})**" for text, url in links.items())
		embed.description = "\n".join(description)
		return embed

	def embed_event(self, title: str, event: Dict[str, str]) -> discord.Embed:
		embed = discord.Embed(
			title=title,
			colour=discord.Colour.green()
		)
		# add overview of event to the embed
		embed.description = self.__get_formatted_event_details(event)
		return embed

	def embed_success(self, title: str) -> discord.Embed:
		return discord.Embed(title=title, colour=discord.Colour.green())

	def __get_formatted_event_details(self, event: Dict[str, str]) -> str:
		return (
			f"**[{event.get('summary')}]({event.get('htmlLink')})**\n" 
			f"{self.__get_formatted_date_range(event)}\n"
		)

	def __get_formatted_date_range(self, event: Dict[str, str]) -> str:
		"""Extract dates from event and convert to readable format"""
		start = event['start'].get('dateTime', event['start'].get('date'))
		end = event['end'].get('dateTime', event['end'].get('date'))
		return f"{self.__format_date(start)} - {self.__format_date(end)}"

	def __format_date(self, date_str: str) -> str:
		"""Convert dates to format: 'Jan 1 2021 1:23 AM'"""
		date = dateparser.parse(
			date_str,
			settings={'TO_TIMEZONE': self.default_time_zone}
		)
		return date.strftime("%b %d %Y %I:%M %p").replace(" 0", " ")