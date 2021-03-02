from datetime import datetime
import os
import re
import discord
import config
from discord.ext import commands
from .calendar_service import CalendarService
from .calendar_embedder import CalendarEmbedder
from .calendar_finder import CalendarFinder
from .calendar_creator import CalendarCreator
from .course_mentions import CourseMentions
from utils.sql_fetcher import SqlFetcher
from .class_role_error import ClassRoleError
from .class_parse_error import ClassParseError
from modules.error.friendly_error import FriendlyError
from utils.utils import is_email, build_aliases, embed_success, wait_for_reaction
from utils.scheduler.scheduler import Scheduler


class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""

	def __init__(self, bot):
		self.bot = bot
		self.calendar_service = CalendarService()
		self.calendar_embedder = CalendarEmbedder()
		self.sql_fetcher = SqlFetcher(os.path.join("modules", "calendar", "queries"))
		self.finder = CalendarFinder(config.conn, self.sql_fetcher)
		self.calendar_creator = CalendarCreator(self.calendar_service, config.conn, self.sql_fetcher)
		self.course_mentions = CourseMentions(config.conn, self.sql_fetcher, bot)
		self.number_emoji = ("0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣")

	@commands.command(
		**build_aliases(
			name="calendar.links",
			prefix=("calendar", "events", "event"),
			suffix=("link", "links"),
		)
	)
	async def calendar_links(self, ctx, *args):
		"""
		Get the links to add or view the calendar

		Usage:
		```
		++calendar.links
		```
		If you have multiple class roles:
		```
		++calendar.links <Class Name>
		```
		Arguments:
		**<Class Name>**: The calendar to get links for (ex. "Lev 2023").
		"""
		try:
			calendar_name = " ".join(args) if args else None
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# fetch links for calendar
		links = self.calendar_service.get_links(calendar.id)
		embed = self.calendar_embedder.embed_link(
			f"🔗 Calendar Links for {calendar.name}", links
		)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.list",
			prefix=("events", "event"),
			suffix=("upcoming", "list", "events", "search", "show", "get"),
			more_aliases=("upcoming", "events", "getevents", "listevents"),
		)
	)
	async def events_list(self, ctx: commands.Context, *args):
		"""
		Display upcoming events from the Google Calendar

		Usage:
		```
		++events.list
		++events.list "<query>"
		++events.list <max_results>
		++events.list "<query>" <max_results>
		++events.list "<query>" <max_results> in <Class Name>
		```
		Arguments:
		**<query>**: The query to search for within event titles. This can be a string to search for or a channel mention. (Default: shows any events)
		**<max_results>**: The maximum number of events to display. (Default: 5 results or 15 with query)
		**<Class Name>**: The calendar to get events from (ex. "Lev 2023"). Only necessary if you have more than one class role.
		"""
		try:
			last_occurence = max(loc for loc, val in enumerate(args) if val == "in") if "in" in args else len(args)
			calendar_name = " ".join(args[last_occurence+1:])
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
			args = args[:last_occurence]
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# all arguments are query if last argument is not a number
		if len(args) > 0 and not args[-1].isdigit():
			query = " ".join(args)
		# all but last argument are query if last argument is a number
		else:
			query = " ".join(args[0:-1]) if len(args) > 1 else ""
		# convert channel mentions to full names
		full_query = self.course_mentions.replace_channel_mentions(query)
		# extract max_results - last argument if it is a number, otherwise, default value
		max_results = 5 # default value if no query
		# last argument if it's a number
		if len(args) > 0 and args[-1].isdigit():
			max_results = int(args[-1])
		# check ahead 15 results by default if there is a query
		elif query:
			max_results = 15
		# fetch events
		events = self.calendar_service.fetch_upcoming(
			calendar.id, max_results, full_query
		)
		embed = self.calendar_embedder.embed_event_list(
			title=f"📅 Upcoming Events for {calendar.name}",
			events=events,
			description=f'Showing results for "{full_query}"' if full_query else "",
		)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.add",
			prefix=("events", "event"),
			suffix=("add", "create", "new"),
			more_aliases=("addevent", "createevent", "newevent"),
		)
	)
	async def add_event(self, ctx: commands.Context, *args):
		"""
		Add events to the Google Calendar

		Usage:
		```
		++events.add <Title> at <Start>
		++events.add <Title> on <Start> to <End>
		++events.add <Title> on <Start> to <End> in <Class Name>
		```
		Examples:
		```
		++events.add #compilers HW 3 on April 10 at 11:59pm
		```
		```
		++events.add Moed A #calculus-1 on February 9 from 9am-11am
		```
		```
		++events.add #digital-systems HW 3 on Apr 15 at 11pm in Lev 2023
		```
		Arguments:
		**<Title>**: The name of the event to add. (You can use channel mentions in here to get fully qualified course names.)
		**<Start>**: The start date and/or time of the event (Israel time).
		**<End>**: The end date and/or time of the event (Israel time). If not specified, the start time is used.
		**<Class Name>**: The calendar to add the event to (ex. "Lev 2023"). Only necessary if you have more than one class role.
		"""
		# replace channel mentions with course names
		message = self.course_mentions.replace_channel_mentions(" ".join(args))
		title = None
		times = None
		# separate title from rest of message
		title_times_separators = (" on ", " at ", " from ", " in ")
		for sep in title_times_separators:
			if sep in message:
				[title, times] = message.split(sep, 1)
				break
		# did not find a way to separate title from rest of message
		if times is None:
			raise FriendlyError(
				"Expected 'on', 'at', 'from', or 'in' to separate title from time.",
				ctx.channel,
				ctx.author,
			)
		# get calendar
		try:
			calendar_name = None
			if " in " in times:
				[times, calendar_name] = times.split(" in ", 1)
			# get calendar specified in arguments
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# default values if no separator found
		start = times
		end = None
		# separate start and end times
		start_end_separators = (" to ", " until ", " for ", "-")
		for sep in start_end_separators:
			if sep in times:
				[start, end] = times.split(sep, 1)
				break
		if " from " in start:
			start = start.replace(" from ", " at ")
		try:
			event = self.calendar_service.add_event(calendar.id, title, start, end)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
			":white_check_mark: Event created successfully", event
		)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.update",
			prefix=("calendar", "events", "event"),
			suffix=("update", "change", "edit"),
			more_aliases=("updateevent", "editevent", "changeevent"),
		)
	)
	async def update_event(self, ctx: commands.Context, *, args=None):
		"""
		Add events to the Google Calendar

		Usage:
		```
		++events.update <query> [parameters to set]
		```
		Examples:
		```
		++events.update "#calculus-1 moed b" title="Moed B #calculus-1" end="12:00 PM"
		```
		```
		++events.update "#calculus-1 review class" start="July 7, 3pm" end="July 7, 5pm"
		```
		```
		++events.update "#digital-systems HW 2" description="Submission box: https://moodle.jct.ac.il/mod/assign/view.php?id=420690"
		```
		```
		++events.update "#calculus-1 moed bet" title="Moed B #calculus-1" in Lev 2023
		```
		Arguments:
		**<query>**: A keyword to look for in event titles. This can be a string to search or include a channel mention.
		**[parameters to set]**: List of parameters in the form `title="new title"`. See below for the list of parameters.
		**<Class Name>**: The calendar to update the event in (ex. "in Lev 2023"). Only necessary if you have more than one class role.

		Allowed parameters (all are optional):
		**title**: The new title of the event.
		**start**: The new start date/time of the event (Israel time).
		**end**: The new end date/time of the event (Israel time).
		**location**: The new location of the event.
		**description**: The new description of the event.
		"""
		# check command syntax
		allowed_params = "|".join(("title", "start", "end", "location", "description"))
		# check for correct pattern in message
		match = re.search(
			r'^\s*\S+\s[\'"]?(?P<query>[^"]*?)[\'"]?,?(?P<params>(?:\s*(?:%s)=\s*"[^"]*?",?)*)(?P<calendar> in \w{3} \d{4})?\s*$'
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
		[query, params, calendar_name] = match.groups()
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(query)
		# get calendar
		try:
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# loading message
		response = await ctx.send(embed=embed_success("🗓 Searching for events..."))
		# get a list of upcoming events
		events = self.calendar_service.fetch_upcoming(calendar.id, 50, query)
		num_events = len(events)
		# no events found
		if num_events == 0:
			await response.delete()
			raise FriendlyError(
				f"No events were found for '{query}'.", ctx.channel, ctx.author
			)
		# multiple events found
		elif num_events > 1:
			embed = self.calendar_embedder.embed_event_list(
				title=f"⚠ Multiple events were found.",
				events=events,
				description=(
					"Please specify which event you would like to update."
					f'\n\nShowing results for "{query}"'
				),
				colour=discord.Colour.gold(),
				enumeration=self.number_emoji,
			)
			await response.edit(embed=embed)
			# ask user to pick an event with emojis
			selection_index = await wait_for_reaction(
				bot=self.bot,
				message=response,
				emoji_list=self.number_emoji[:num_events],
				allowed_users=[ctx.author],
			)
			# get the event selected by the user
			event_to_update = events[selection_index]
		# only 1 event found
		else:
			# get the event at index 0
			event_to_update = events[0]
		# Extract params into kwargs
		param_args = dict(
			re.findall(
				r'(?P<key>%s)\s*=\s*"(?P<value>[^"]*?)"' % allowed_params, params,
			)
		)
		# Replace channel mentions with full names
		for key, value in param_args.items():
			param_args[key] = self.course_mentions.replace_channel_mentions(value)
		try:
			event = self.calendar_service.update_event(
				calendar.id, event_to_update, **param_args
			)
		except ValueError as error:
			await response.delete()
			raise FriendlyError(error.args[0], ctx.channel, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
			":white_check_mark: Event updated successfully", event
		)
		await response.edit(embed=embed)

	@commands.command(
		**build_aliases(
			name="events.delete",
			prefix=("calendar", "events", "event"),
			suffix=("delete", "remove"),
			more_aliases=("deleteevent", "removeevent"),
		)
	)
	async def delete_event(self, ctx: commands.Context, *args):
		"""
		Add events to the Google Calendar

		Usage:
		```
		++events.delete <query>
		++events.delete <query> in <Class Name>
		```
		Example:
		```
		++events.delete #calculus-1 Moed Bet
		++events.delete #digital-systems HW 10 in Lev 2023
		```
		Arguments:
		**<query>**: A keyword to look for in event titles. This can be a string to search or include a channel mention.
		**<Class Name>**: The calendar to delete the event from (ex. "Lev 2023"). Only necessary if you have more than one class role.
		"""
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(" ".join(args))
		match = re.search(r"^\s*(.*?)\s*(in \w{3} \d{4})?\s*$", query)
		[query, calendar_name] = match.groups() if match is not None else [None, None]

		# get calendar
		try:
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# loading message
		response = await ctx.send(embed=embed_success("🗓 Searching for events..."))
		# fetch upcoming events
		events = self.calendar_service.fetch_upcoming(calendar.id, 50, query)
		num_events = len(events)
		# no events found
		if num_events == 0:
			await response.delete()
			raise FriendlyError(
				f"No events were found for '{query}'.", ctx.channel, ctx.author
			)
		# multiple events found
		elif num_events > 1:
			embed = self.calendar_embedder.embed_event_list(
				title=f"⚠ Multiple events were found.",
				events=events,
				description=(
					'Please specify which event you would like to delete.'
					f'\n\nShowing results for "{query}"'
				),
				colour=discord.Colour.gold(),
				enumeration=self.number_emoji,
			)
			await response.edit(embed=embed)
			# ask user to pick an event with emojis
			selection_index = await wait_for_reaction(
				bot=self.bot,
				message=response,
				emoji_list=self.number_emoji[:num_events],
				allowed_users=[ctx.author],
			)
			# get the event selected by the user
			event_to_delete = events[selection_index]
		# only 1 event found
		else:
			# get the event at index 0 if there's only 1
			event_to_delete = events[0]
		# delete event
		try:
			self.calendar_service.delete_event(calendar.id, event_to_delete)
		except ConnectionError as error:
			await response.delete()
			raise FriendlyError(error.args[0], ctx.channel, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
			"🗑 Event deleted successfully", event_to_delete
		)
		await response.edit(embed=embed)

	@commands.command(
		**build_aliases(
			name="calendar.grant",
			prefix=("calendar", "events"),
			suffix=("grant", "manage", "allow", "invite"),
		)
	)
	async def addmanager(self, ctx: commands.Context, *args):
		"""
		Add a Google account as a manager of your class's calendar(s)

		Usage:
		```
		++calendar.grant <email>
		```
		If you have more than one class role:
		```
		++calendar.grant <email> <Class Name>
		```
		Arguments:
		**<email>**: Email address to add as a calendar manager.
		**<Class Name>**: The calendar to grant access to (ex. "Lev 2023"). Only necessary if you have more than one class role.
		"""
		# check if calendar was specified
		calendar_match = re.search(r"\b(\w{3} \d{4})", " ".join(args))
		# get calendar
		try:
			calendar_name = calendar_match.groups()[0] if calendar_match else None
			calendar = self.finder.get_calendar(ctx.author, calendar_name)
		except (ClassRoleError, ClassParseError) as error:
			raise FriendlyError(error.args[0], ctx.channel, ctx.author)
		# validate email address
		email = args[0]
		if not is_email(email):
			raise FriendlyError("Invalid email address", ctx.channel, ctx.author)
		# add manager to calendar
		if self.calendar_service.add_manager(calendar.id, email):
			embed = embed_success(
				f":office_worker: Successfully added manager to {calendar.name}."
			)
			await ctx.send(embed=embed)
		else:
			raise FriendlyError(
				"An error occurred while applying changes.", ctx.channel, ctx.author
			)

	@commands.command(
		**build_aliases(
			name="calendars.create",
			prefix=("calendar", "calendars"),
			suffix=("add", "create", "new"),
			more_aliases=["createcalendar"],
		)
	)
	@commands.has_permissions(manage_roles=True)
	async def createcalendar(self, ctx: commands.Context, *args):
		"""
		Create a public calendar on the service account

		Usage:
		```
		++calendars.create "JCT CompSci Lev 2020"
		```
		Arguments:
		> **JCT CompSci Lev 2020**: name of the calendar to create

		**Note:** to use this command, the user must have permission to manage roles.
		"""
		name = " ".join(args)
		# create calendar
		new_calendar = self.calendar_service.create_calendar(name)
		embed = embed_success(
			f"📆 Successfully created '{new_calendar.name}' calendar.",
			f"Calendar ID: {new_calendar.id}",
		)
		await ctx.send(embed=embed)

	@commands.command(
		**build_aliases(
			name="calendars.list",
			prefix=("calendar", "calendars"),
			suffix=("list", "show", "get"),
			more_aliases=["listcalendars"],
		)
	)
	@commands.has_permissions(manage_roles=True)
	async def listcalendars(self, ctx):
		"""
		Get a list of all calendars on the service account

		Usage:
		```
		++calendars.list
		```
		**Note:** to use this command, the user must have permission to manage roles.
		"""
		# get calendar list
		calendars = self.calendar_service.get_calendar_list()
		details = (f"{calendar.name}: {calendar.id}" for calendar in calendars)
		await ctx.send("\n".join(details))

	@Scheduler.schedule(1)
	async def on_new_academic_year(self):
		"""Create calendars for each campus and update the database"""
		year = datetime.now().year + 3
		self.calendar_creator.create_class_calendars(year)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))
