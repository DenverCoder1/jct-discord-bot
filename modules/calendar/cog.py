import os
import re
import config
from discord.ext import commands
from .calendar import Calendar
from .calendar_embedder import CalendarEmbedder
from .calendar_finder import CalendarFinder
from .course_mentions import CourseMentions
from utils.sql_fetcher import SqlFetcher
from .class_role_error import ClassRoleError
from .class_parse_error import ClassParseError
from modules.error.friendly_error import FriendlyError
from utils.utils import is_email, build_aliases


class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""

	def __init__(self, bot):
		self.bot = bot
		self.calendar = Calendar()
		self.calendar_embedder = CalendarEmbedder()
		self.sql_fetcher = SqlFetcher(os.path.join("modules", "calendar", "queries"))
		self.finder = CalendarFinder(config.conn, self.sql_fetcher)
		self.course_mentions = CourseMentions(config.conn, self.sql_fetcher, bot)

	@commands.command(
		**build_aliases(
			name="calendar.links",
			prefix=("calendar", "events", "event"),
			suffix=("link", "links"),
		)
	)
	async def calendar_links(self, ctx):
		"""
		Get the links to add or view the calendar

		Usage:
		```
		++calendar.links
		```
		"""
		class_roles = self.finder.get_class_roles(ctx.author)
		for grad_year, campus in class_roles:
			calendar_id = self.finder.get_calendar_id(grad_year, campus)
			if calendar_id is None:
				raise FriendlyError(
					f"No calendar found for {campus} {grad_year}",
					ctx.channel,
					ctx.author,
				)
			links = self.calendar.get_links(calendar_id)
			embed = self.calendar_embedder.embed_link(
				f"Calendar Links for {campus} {grad_year}", links
			)
			await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.list",
			prefix=("calendar", "events", "event"),
			suffix=("upcoming", "list", "events", "search"),
			more_aliases=("upcoming", "events"),
		)
	)
	async def events_list(self, ctx, *args):
		"""
		Display upcoming events from the Google Calendar

		Usage:
		```
		++events.list
		++events.list <query>
		++events.list <max_results>
		++events.list <query> <max_results>
		```
		Arguments:
		**<query>**: The query to search for within event titles. This can be a string to search for or a channel mention. (Default: shows any events)
		**<max_results>**: The maximum number of events to display. (Default: 5 results or 15 with query)
		"""
		# convert channel mentions to full names
		args = list(map(self.course_mentions.map_channel_mention, args))
		# extract query string
		query = (
			# all arguments are query if last argument is not a number
			" ".join(args)
			if len(args) > 0 and not args[-1].isdigit()
			# all but last argument are query if last argument is a number
			else " ".join(args[0:-1])
			if len(args) > 1
			# no query if no arguments or only 1 argument and it's a number
			else ""
		)
		# extract max_results - last argument if it is a number, otherwise, default value
		max_results = (
			# last argument if it's a number
			args[-1]
			if len(args) > 0 and args[-1].isdigit()
			# check for 5 results by default if there is no query
			else 5
			if query == ""
			# check ahead 15 results by default if there is a query
			else 15
		)
		# get class roles of the author
		class_roles = self.finder.get_class_roles(ctx.author)
		for grad_year, campus in class_roles:
			# display events for each calendar
			calendar_id = self.finder.get_calendar_id(grad_year, campus)
			events = self.calendar.fetch_upcoming(calendar_id, max_results, query)
			embed = self.calendar_embedder.embed_event_list(
				f"Upcoming Events for {campus} {grad_year}", events, query
			)
			await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.add",
			prefix=("calendar", "events", "event"),
			suffix=("add", "create", "new"),
			more_aliases=("addevent", "createevent", "newevent"),
		)
	)
	async def add_event(self, ctx, *args):
		"""
		Add events to the Google Calendar

		Usage:
		```
		++events.add <Title> at <Start>
		++events.add <Title> on <Start>
		++events.add <Title> on <Start> to <End>
		++events.add <Title> on <Start> to <End> in <Class Name>
		```
		Examples:
		```
		++events.add Compilers HW 3 on April 10 at 11:59pm
		++events.add Calculus Moed Alef on February 9, 2021 at 8:30 am to 10:30 am
		++events.add Compilers HW 3 on April 10 at 11:59pm in Lev 2023
		```
		Arguments:
		**<Title>**: The name of the event to add. (You can use channel mentions in here to get fully qualified course names.)
		**<Start>**: The start date and/or time of the event (Israel time).
		**<End>**: The end date and/or time of the event (Israel time). If not specified, the start time is used.
		**<Class Name>**: The calendar to add the event to. Only necessary if you have more than one class role.
		"""
		# replace channel mentions with course names
		message = " ".join(map(self.course_mentions.map_channel_mention, args))
		grad_year = None
		campus = None
		title = None
		times = None
		# separate title from rest of message
		title_times_separators = [" on ", " at "]
		for sep in title_times_separators:
			if sep in message:
				[title, times] = message.split(sep, 1)
				break
		# did not find a way to separate title from rest of message
		if times is None:
			raise FriendlyError(
				"Expected 'on' or 'at' to separate title from time.",
				ctx.channel,
				ctx.author,
			)
		# check if calendar specified at the end
		if " in " in times:
			[times, calendar] = times.split(" in ", 1)
			try:
				grad_year, campus = self.finder.extract_year_and_campus(calendar)
				# check that specified calendar is one of the user's roles
				class_roles = self.finder.get_class_roles(ctx.author)
				if (grad_year, campus) not in class_roles:
					raise ClassRoleError(
						"You can not add events to the calendar of another class."
					)
			except (ClassRoleError, ClassParseError) as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# default values if no separator found
		start = times
		end = None
		# separate start and end times
		start_end_separators = [" to ", " until ", " for ", "-"]
		for sep in start_end_separators:
			if sep in times:
				[start, end] = times.split(sep, 1)
				break
		if grad_year is None or campus is None:
			try:
				grad_year, campus = self.finder.get_class_info_from_role(ctx.author)
			except ClassRoleError as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		if " from " in start:
			start = start.replace(" from ", " at ")
		calendar_id = self.finder.get_calendar_id(grad_year, campus)
		try:
			event = self.calendar.add_event(calendar_id, title, start, end)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author, error)
		embed = self.calendar_embedder.embed_event("Event created successfully", event)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.update",
			prefix=("calendar", "events", "event"),
			suffix=("update", "change", "edit"),
			more_aliases=("updateevent", "editevent", "changeevent"),
		)
	)
	async def update_event(self, ctx, *, args=None):
		"""
		Add events to the Google Calendar

		Usage:
		```
		++events.update "<query>" [params to set]
		++events.update "<query>" [params to set] in <Class Name>
		```
		Examples:
		```
		++events.update "calc moed b" title="Moed B #calculus-1"
		++events.update "#calculus-1 review class" start="July 7, 3pm" end="July 7, 5pm"
		++events.update "#digital-systems HW 2" description="Submission box: https://moodle.jct.ac.il/mod/assign/view.php?id=420690"
		++events.update "calc moed b" title="Moed B #calculus-1" in Lev 2023
		```
		Arguments:
		**<query>**: The query to search for within event titles. This can be a string to search or include a channel mention.
		**<Class Name>**: The calendar to add the event to. Only necessary if you have more than one class role.

		Set parameters (all are optional):
		**title**: The new title of the event.
		**start**: The new start date and time of the event (Israel time).
		**end**: The new end date and time of the event (Israel time).
		**location**: The new location of the event.
		**description**: The new description of the event.
		"""
		# check command syntax
		allowed_params = "|".join(("title", "start", "end", "location", "description"))
		# check for correct pattern in message
		match = re.search(
			r'^\s*\S+\s[\'"]?(?P<query>[^"]*?)[\'"]?,?(?P<params>(?:\s+(?:%s)=[\'"]?[^"]*?[\'"]?,?)*)(?P<calendar>\sin\s\w+\s\d{4})?\s*$'
			% allowed_params,
			ctx.message.content,
		)
		if match is None:
			# did not fit pattern required for update command
			raise FriendlyError(
				"Could not figure out command syntax. Check the examples with"
				f" `{ctx.prefix}help {ctx.invoked_with}`",
				ctx.channel,
				ctx.author,
			)
		# extract query, params list, and calendar from the command
		[query, params, calendar] = match.groups()
		# replace channel mentions with course names
		query = " ".join(map(self.course_mentions.map_channel_mention, query.split()))
		grad_year = None
		campus = None
		if calendar is not None:
			try:
				grad_year, campus = self.finder.extract_year_and_campus(calendar)
				# check that specified calendar is one of the user's roles
				class_roles = self.finder.get_class_roles(ctx.author)
				if (grad_year, campus) not in class_roles:
					raise ClassRoleError(
						"You can not add events to the calendar of another class."
					)
			except (ClassRoleError, ClassParseError) as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		if grad_year is None or campus is None:
			try:
				grad_year, campus = self.finder.get_class_info_from_role(ctx.author)
			except ClassRoleError as error:
				raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		calendar_id = self.finder.get_calendar_id(grad_year, campus)
		events = self.calendar.fetch_upcoming(calendar_id, 50, query)
		if len(events) == 0:
			raise FriendlyError(
				f"No events were found for '{query}'.", ctx.channel, ctx.author
			)
		if len(events) > 1:
			# TODO: Allow user to choose an event
			embed = self.calendar_embedder.embed_event_list(
				f"Multiple events were found.", events, query
			)
			return await ctx.send(embed=embed)
		# Extract params into kwargs
		param_args = dict(
			re.findall(
				r'(?P<key>%s)\s*=\s*[\'"]?(?P<value>[^"]*?)[\'"]?' % allowed_params,
				params,
			)
		)
		event = self.calendar.udpate_event(calendar_id, events[0], **param_args)
		embed = self.calendar_embedder.embed_event("Event updated successfully", event)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="calendar.grant",
			prefix=("calendar", "events"),
			suffix=("grant", "manage", "allow", "invite"),
		)
	)
	async def addmanager(self, ctx, email):
		"""
		Add a Google account as a manager of your class's calendar

		Usage:
		```
		++calendar.grant <email>
		```
		Arguments:
		> **<email>**: Email address to add as a calendar manager
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
	@commands.has_permissions(manage_roles=True)
	async def createcalendar(self, ctx, *args):
		"""
		Create a public calendar on the service account

		Usage:
		```
		++createcalendar JCT CompSci Lev 2020
		```
		Arguments:
		> **JCT CompSci Lev 2020**: name of the calendar to create
		"""
		name = " ".join(args)
		# create calendar
		new_calendar = self.calendar.create_calendar(name)
		embed = self.calendar_embedder.embed_success(
			f"Successfully created '{new_calendar['summary']}' calendar.",
			f"Calendar ID: {new_calendar['id']}",
		)
		await ctx.send(embed=embed)

	@commands.command(name="listcalendars")
	@commands.has_permissions(manage_roles=True)
	async def listcalendars(self, ctx):
		"""
		Get a list of all calendars on the service account

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
