from discord.ext import commands
from .calendar import Calendar
from .calendar_embedder import CalendarEmbedder

class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""
	def __init__(self, bot):
		self.bot = bot
		self.calendar = Calendar()
		self.calendar_embedder = CalendarEmbedder()

	@commands.command(name="calendarlinks", aliases=["calendarlink", "links"])
	async def calendarlinks(self, ctx):
		"""
		Command to get the link to add the calendar to a Google Calendar account

		Usage:
		```
		++calendarlinks
		```
		"""
		links = self.calendar.get_links()
		embed = self.calendar_embedder.embed_link("Calendar Links", links)
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
		embed = self.calendar_embedder.embed_event_list("Upcoming Events", events)
		await ctx.send(embed=embed)

	@commands.command(name="addevent")
	async def addevent(self, ctx, *args):
		"""
		Command to display upcoming events from the Google Calendar

		Usage:
		```
		++addevent AOOPD Moed Alef on February 9, 2021 at 8:30 am to 10:30 am
		```
		"""
		message = " ".join(args)
		if ' on ' in message and ' to ' in message:
			[summary, times] = message.split(' on ', 2)
			[start, end] = times.split(' to ', 2)
			event = self.calendar.add_event(summary, start, end)
			embed = self.calendar_embedder.embed_event("Event created successfully", event)
			await ctx.send(embed=embed)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))