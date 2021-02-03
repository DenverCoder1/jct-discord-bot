from typing import Iterable
import discord
import dateparser

class EventFormatter:
	def __init__(self):
		self.default_time_zone = "Asia/Jerusalem"

	def format_event_list(self, title: str, events: Iterable[dict]) -> discord.Embed:
		"""Generates an embed with a field for each event in the given list"""
		embed = discord.Embed(
			title=title,
			colour=discord.Colour.green()
		)
		if not events:
			embed.description = "No events found"
		else:
			# add events to embed
			for event in events:
				embed.add_field(
					name=event['summary'], 
					value=self.get_formatted_date_range(event)
				)
		embed.set_footer(text=f"Times are shown for {self.default_time_zone}")
		return embed

	def get_formatted_date_range(self, event: dict) -> str:
		"""Extract dates from event and convert to readable format"""
		start = event['start'].get('dateTime', event['start'].get('date'))
		end = event['end'].get('dateTime', event['end'].get('date'))
		return f"{self.__format_date(start)} - {self.__format_date(end)}"

	def __format_date(self, date_str: str) -> str:
		"""Convert dates to format: 'Jan 1 2021 1:23 AM'"""
		date = dateparser.parse(date_str, settings={'TO_TIMEZONE': self.default_time_zone})
		return date.strftime("%b %d %Y %I:%M %p").replace(" 0", " ")