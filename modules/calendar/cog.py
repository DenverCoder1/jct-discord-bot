from discord.ext import commands
from .calendar import Calendar
from .event_formatter import EventFormatter

class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""
	def __init__(self, bot):
		self.bot = bot
		self.calendar = Calendar()
		self.event_formatter = EventFormatter()

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