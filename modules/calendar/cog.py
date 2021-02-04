from discord.ext import commands
from .calendar import Calendar
from .calendar_embedder import CalendarEmbedder
from modules.error.friendly_error import FriendlyError
from utils.utils import is_email

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

	@commands.command(name="addmanager", aliases=["add_manager", "addcalendarmanager"])
	async def addmanager(self, ctx, email):
		"""
		Command to display upcoming events from the Google Calendar

		Usage:
		```
		++addmanager email
		```
		Arguments:
		> **email**: Email address to add as a calendar manager
		"""
		if not is_email(email):
			raise FriendlyError("Invalid email address", ctx.channel, ctx.author)
		# TODO: get calendar based on role
		calendar = "JCT CompSci ESP"
		# add manager to calendar
		self.calendar.add_manager(email)
		embed = self.calendar_embedder.embed_success(f"Successfully added manager to {calendar}")
		await ctx.send(embed=embed)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))