from discord.ext import commands
from .calendar import Calendar
from .event_formatter import EventFormatter

class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""
	def __init__(self, bot):
		self.bot = bot
		self.calendar = Calendar()
		self.event_formatter = EventFormatter()

	@commands.command(name="calendarlinks", aliases=["calendarlink","calendar_links"])
	async def calendarlinks(self, ctx):
		"""
		Command to get the link to add the calendar to a Google Calendar account

		Usage:
		```
		++calendarlinks
		```
		"""
		links = self.calendar.get_links()
		embed = self.event_formatter.embed_link("Calendar Links", links)
		await ctx.send(embed=embed)

	@commands.command(name="upcoming")
	async def upcoming(self, ctx):
		"""
		Command to display upcoming events from the Google Calendar

		Usage:
		```
		++upcoming
		```
		"""
		events = self.calendar.fetch_upcoming()
		embed = self.event_formatter.format_event_list("Upcoming Events", events)
		await ctx.send(embed=embed)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))