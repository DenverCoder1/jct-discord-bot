import os
import config
from discord.ext import commands
from .calendar import Calendar
from .calendar_embedder import CalendarEmbedder
from .calendar_finder import CalendarFinder
from utils.sql_fetcher import SqlFetcher
from .class_role_error import ClassRoleError
from .class_parse_error import ClassParseError
from modules.error.friendly_error import FriendlyError
from utils.utils import is_email


class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""

	def __init__(self, bot):
		self.bot = bot
		self.calendar = Calendar()
		self.calendar_embedder = CalendarEmbedder()
		self.sql_fetcher = SqlFetcher(os.path.join("modules", "calendar", "queries"))
		self.finder = CalendarFinder(config.conn, self.sql_fetcher)

	@commands.command(name="calendarlinks", aliases=["calendarlink", "links"])
	async def calendarlinks(self, ctx):
		"""
		Command to get the links to add the calendar to a Google Calendar account

		Usage:
		```
		++calendarlinks
		```
		"""
		class_roles = self.finder.get_class_roles(ctx.author)
		for grad_year, campus in class_roles:
			calendar_id = self.finder.get_calendar_id(grad_year, campus)
			links = self.calendar.get_links(calendar_id)
			embed = self.calendar_embedder.embed_link(
				f"Calendar Links for {campus} {grad_year}", links
			)
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
		class_roles = self.finder.get_class_roles(ctx.author)
		for grad_year, campus in class_roles:
			calendar_id = self.finder.get_calendar_id(grad_year, campus)
			events = self.calendar.fetch_upcoming(calendar_id)
			embed = self.calendar_embedder.embed_event_list(
				f"Upcoming Events for {campus} {grad_year}", events
			)
			await ctx.send(embed=embed)

	@commands.command(name="addevent")
	async def addevent(self, ctx, *args):
		"""
		Command to add events to the Google Calendar.

		Usage:
		```
		++addevent [Subject] on [Start Time]
		++addevent [Subject] on [Start Time] to <End Time>
		++addevent [Subject] on [Start Time] to <End Time> in <Class Name>
		```
		Examples:
		```
		++addevent Compilers HW 3 on April 10 at 11:59pm
		++addevent Calculus Moed Alef on February 9, 2021 at 8:30 am to 10:30 am
		++addevent Compilers HW 3 on April 10 at 11:59pm in Lev 2023
		```
		Arguments:
		**[Subject]** - the name of the event to add
		**[Start Time]** - start time of the event
		**<End Time>** (optional) - end time of the event. \
			If not specified, start time is used.
		**<Class Name>** (optional) - calendar to add the event to. \
			Only necessary if you have more than one class role.
		"""
		message = " ".join(args)
		grad_year = None
		campus = None
		summary = None
		times = None
		if " on " in message:
			# separate summary from rest of message
			[summary, times] = message.split(" on ", 2)
		elif " at " in message:
			[summary, times] = message.split(" at ", 2)
		if not times:
			raise FriendlyError(
				"Expected 'on' or 'at' to separate subject from time.",
				ctx.channel,
				ctx.author,
			)
		# check if calendar specified at the end
		if " in " in times:
			[times, calendar] = times.split(" in ")
			try:
				grad_year, campus = self.finder.extract_year_and_campus(calendar)
				# check that specified calendar is one of the user's roles
				# TODO: permit admins to add to other calendars
				class_roles = self.finder.get_class_roles(ctx.author)
				if (grad_year, campus) not in class_roles:
					raise ClassRoleError(
						"You do not have permission to add to that calendar."
					)
			except (ClassRoleError, ClassParseError) as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# separate start and end times
		if " to " in times:
			[start, end] = times.split(" to ", 2)
		else:
			start = times
			end = None
		if not grad_year or not campus:
			try:
				grad_year, campus = self.finder.get_class_info_from_role(ctx.author)
			except ClassRoleError as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		calendar_id = self.finder.get_calendar_id(grad_year, campus)
		event = self.calendar.add_event(calendar_id, summary, start, end)
		embed = self.calendar_embedder.embed_event("Event created successfully", event)
		await ctx.send(embed=embed)

	@commands.command(name="addmanager", aliases=["add_manager", "addcalendarmanager"])
	async def addmanager(self, ctx, email):
		"""
		Command to add a Google account as a manager of your class's calendar

		Usage:
		```
		++addmanager email
		```
		Arguments:
		> **email**: Email address to add as a calendar manager
		"""
		if not is_email(email):
			raise FriendlyError("Invalid email address", ctx.channel, ctx.author)
		class_roles = self.finder.get_class_roles(ctx.author)
		for grad_year, campus in class_roles:
			calendar_id = self.finder.get_calendar_id(grad_year, campus)
			# add manager to calendar
			self.calendar.add_manager(calendar_id, email)
			embed = self.calendar_embedder.embed_success(
				f"Successfully added manager to {campus} {grad_year} calendar."
			)
			await ctx.send(embed=embed)

	@commands.command(name="createcalendar")
	@commands.has_permissions(manage_server=True)
	async def createcalendar(self, ctx, *args):
		"""
		Command to create a public calendar on the service account

		Usage:
		```
		++createcalendar JCT CompSci Lev 2020
		```
		Arguments:
		> **JCT CompSci Lev 2020**: name of the calendar to create
		"""
		summary = " ".join(args)
		# create calendar
		new_calendar = self.calendar.create_calendar(summary)
		embed = self.calendar_embedder.embed_success(
			f"Successfully created '{new_calendar['summary']}' calendar.",
			f"Calendar ID: {new_calendar['id']}",
		)
		await ctx.send(embed=embed)

	@commands.command(name="listcalendars")
	@commands.has_permissions(manage_server=True)
	async def listcalendars(self, ctx):
		"""
		Command to get a list of all calendars on the service account

		Usage:
		```
		++listcalendars
		```
		"""
		# get calendar list
		calendars = self.calendar.get_calendar_list()
		details = (f"{calendar['summary']}: {calendar['id']}" for calendar in calendars)
		await ctx.send("\n".join(details))


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))