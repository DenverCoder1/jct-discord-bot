from datetime import datetime
from typing import Optional
import config
from discord.ext import commands
from .calendar import Calendar
from .calendar_service import CalendarService
from .calendar_embedder import CalendarEmbedder
from .calendar_creator import CalendarCreator
from .course_mentions import CourseMentions
from modules.error.friendly_error import FriendlyError
from utils.embedder import embed_success
from utils.utils import is_email
from utils.scheduler import Scheduler
from database.group import Group
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice

groups = Group.get_groups()


class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		timezone = "Asia/Jerusalem"
		self.embedder = CalendarEmbedder(bot, timezone)
		self.service = CalendarService(timezone)
		self.creator = CalendarCreator(self.service, config.conn)
		self.course_mentions = CourseMentions(config.conn, bot)
		self.groups = groups

	@cog_ext.cog_subcommand(
		base="calendar",
		name="links",
		description="Get the links to add or view the calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def calendar_links(self, ctx: SlashContext, class_name: Optional[int] = None):
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		# fetch links for calendar
		links = self.service.get_links(calendar)
		embed = self.embedder.embed_links(
			f"🔗 Calendar Links for {calendar.name}", links
		)
		await ctx.send(embed=embed)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="events",
		description="Display upcoming events from the Google Calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="query",
				description=(
					"Query or channel mention to search for within event titles (if not"
					" specified, shows all events)"
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="results_per_page",
				description="Number of events to display per page. (Default: 5)",
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
			),
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def events(
		self,
		ctx: SlashContext,
		query: str = "",
		results_per_page: int = 5,
		class_name: Optional[int] = None,
	):
		await ctx.defer()
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		# convert channel mentions to full names
		full_query = self.course_mentions.replace_channel_mentions(query)
		# fetch upcoming events
		events = self.service.fetch_upcoming(calendar.id, full_query)
		# display events and allow showing more with reactions
		await self.embedder.embed_event_pages(
			ctx, events, full_query, results_per_page, calendar
		)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="add",
		description="Add events to the Google Calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="title",
				description='Title of the event (eg. "HW 1 #statistics")',
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="start",
				description=(
					'The start date of the event in Israel Time (eg. "April 15, 2pm")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="end",
				description='The end date of the event in Israel Time (eg. "3pm")',
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="description",
				description=(
					'The description of the event (eg. "Submission box:'
					' https://moodle.jct.ac.il/123")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="location",
				description='The location of the event (eg. "Brause 305")',
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def event_add(
		self,
		ctx: SlashContext,
		title: str,
		start: str,
		end: Optional[str] = None,
		description: str = "",
		location: str = "",
		class_name: Optional[int] = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		title = self.course_mentions.replace_channel_mentions(title)
		description = self.course_mentions.replace_channel_mentions(description)
		location = self.course_mentions.replace_channel_mentions(location)
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		try:
			event = self.service.add_event(
				calendar.id, title, start, end, description, location
			)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.embedder.embed_event(
			":white_check_mark: Event created successfully", event
		)
		await ctx.send(embed=embed)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="update",
		description="Update events in the Google Calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="query",
				description=(
					"Query or channel mention to search for within event titles"
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="title",
				description='New title of the event (eg. "HW 1 #statistics")',
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="start",
				description=(
					'New start date of the event in Israel Time (eg. "April 15, 2pm")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="end",
				description='New end date of the event in Israel Time (eg. "3pm")',
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="description",
				description=(
					'New description of the event (eg. "Submission box:'
					' https://moodle.jct.ac.il/123")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="location",
				description='The location of the event (eg. "Brause 305")',
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def event_update(
		self,
		ctx: SlashContext,
		query: str,
		title: Optional[str] = None,
		start: Optional[str] = None,
		end: Optional[str] = None,
		description=None,
		location=None,
		class_name: Optional[int] = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		# get a list of upcoming events
		events = self.service.fetch_upcoming(calendar.id, query)
		# get event to update
		event_to_update = await self.embedder.get_event_choice(
			ctx, events, query, "update"
		)
		# replace channel mentions
		if title is not None:
			title = self.course_mentions.replace_channel_mentions(title)
		if description is not None:
			description = self.course_mentions.replace_channel_mentions(description)
		if location is not None:
			location = self.course_mentions.replace_channel_mentions(location)
		try:
			event = self.service.update_event(
				calendar.id, event_to_update, title, start, end, description, location,
			)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.embedder.embed_event(
			":white_check_mark: Event updated successfully", event
		)
		# edit message if sent already, otherwise send
		sender = ctx.send if ctx.message is None else ctx.message.edit
		await sender(embed=embed)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="delete",
		description="Delete events from the Google Calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="query",
				description=(
					"Query or channel mention to search for within event titles"
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def event_delete(
		self, ctx: SlashContext, query: str, class_name: Optional[int] = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		# fetch upcoming events
		events = self.service.fetch_upcoming(calendar.id, query)
		# get event to delete
		event_to_delete = await self.embedder.get_event_choice(
			ctx, events, query, "delete"
		)
		# delete event
		try:
			self.service.delete_event(calendar.id, event_to_delete)
		except ConnectionError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.embedder.embed_event(
			"🗑 Event deleted successfully", event_to_delete
		)
		# edit message if sent already, otherwise send
		sender = ctx.send if ctx.message is None else ctx.message.edit
		await sender(embed=embed)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="grant",
		description="Add a Google account as a manager of your class's calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="email",
				description="The email address of the Google account to add",
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Leave blank if you"
					" have only one class role."
				),
				option_type=SlashCommandOptionType.INTEGER,
				required=False,
				choices=[
					create_choice(name=group.name, value=group.id) for group in groups
				],
			),
		],
	)
	async def calendar_grant(
		self, ctx: SlashContext, email: str, class_name: Optional[int] = None,
	):
		await ctx.defer()
		# get calendar from selected class_role or author
		calendar = Calendar.get_calendar(ctx, self.groups, class_name)
		# validate email address
		if not is_email(email):
			raise FriendlyError("Invalid email address", ctx, ctx.author)
		# add manager to calendar
		if self.service.add_manager(calendar.id, email):
			embed = embed_success(
				f":office_worker: Successfully added manager to {calendar.name}."
			)
			await ctx.send(embed=embed)
			return
		raise FriendlyError(
			"An error occurred while applying changes.", ctx, ctx.author
		)

	@Scheduler.schedule(1)
	async def on_new_academic_year(self):
		"""Create calendars for each campus and update the database"""
		year = datetime.now().year + 3
		self.creator.create_class_calendars(year)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))
