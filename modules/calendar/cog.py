from datetime import datetime
import discord
import config
from discord.ext import commands
from .calendar_service import CalendarService
from .calendar_embedder import CalendarEmbedder
from .calendar_finder import CalendarFinder
from .calendar_creator import CalendarCreator
from .course_mentions import CourseMentions
from modules.error.friendly_error import FriendlyError
from utils.embedder import embed_success
from utils.utils import is_email, wait_for_reaction
from utils.scheduler.scheduler import Scheduler
from utils.class_role.class_role import ClassRole
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice


class CalendarCog(commands.Cog, name="Calendar"):
	"""Display and update Google Calendar events"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.calendar_embedder = CalendarEmbedder(bot)
		self.calendar_service = CalendarService()
		self.sql_fetcher = config.sql_fetcher
		self.finder = CalendarFinder(config.conn, self.sql_fetcher)
		self.calendar_creator = CalendarCreator(
			self.calendar_service, config.conn, self.sql_fetcher
		)
		self.course_mentions = CourseMentions(config.conn, self.sql_fetcher, bot)
		self.number_emoji = (
			"0️⃣",
			"1️⃣",
			"2️⃣",
			"3️⃣",
			"4️⃣",
			"5️⃣",
			"6️⃣",
			"7️⃣",
			"8️⃣",
			"9️⃣",
		)

	@cog_ext.cog_subcommand(
		base="calendar",
		name="links",
		description="Get the links to add or view the calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				# option returns class_name and calendar as value
				name="class_name",
				description=(
					"Calendar to show events for (eg. Lev 2023). Only necessary if you"
					" have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def calendar_links(self, ctx: SlashContext, class_role: str = None):
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		# fetch links for calendar
		links = self.calendar_service.get_links(calendar.id)
		embed = self.calendar_embedder.embed_link(
			f"🔗 Calendar Links for {calendar.name}", links
		)
		await ctx.send(embed=embed)

	@cog_ext.cog_subcommand(
		base="events",
		name="list",
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
				# option returns class role and calendar as value
				name="class_role",
				description=(
					"Calendar to show events for (eg. Lev 2023). Only necessary if you"
					" have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def events(
		self,
		ctx: SlashContext,
		query: str = "",
		results_per_page: int = 5,
		class_role: str = None,
	):
		await ctx.defer()
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		# convert channel mentions to full names
		full_query = self.course_mentions.replace_channel_mentions(query)
		# fetch upcoming events
		events = self.calendar_service.fetch_upcoming(calendar.id, full_query)
		# display events and allow showing more with reactions
		await self.calendar_embedder.embed_event_pages(
			ctx, events, full_query, results_per_page, calendar
		)

	@cog_ext.cog_subcommand(
		base="events",
		name="add",
		description="Add events to the Google Calendar",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="title",
				description='Title of the event (eg. "HW 1 #linear-algebra")',
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
				# option returns class role and calendar as value
				name="class_role",
				description=(
					"Calendar to show events for (eg. Lev 2023). Only necessary if you"
					" have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def event_add(
		self,
		ctx: SlashContext,
		title: str,
		start: str,
		end: str = None,
		description: str = "",
		location: str = "",
		class_role: str = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		title = self.course_mentions.replace_channel_mentions(title)
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		try:
			event = self.calendar_service.add_event(
				calendar.id, title, start, end, location, description
			)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
			":white_check_mark: Event created successfully", event
		)
		await ctx.send(embed=embed)

	@cog_ext.cog_subcommand(
		base="events",
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
				description='New title of the event (eg. "HW 1 #linear-algebra")',
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
				# option returns class role and calendar as value
				name="class_role",
				description=(
					"Calendar to look for events in (eg. Lev 2023). Only necessary if"
					" you have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def event_update(
		self,
		ctx: SlashContext,
		query: str,
		title: str = None,
		start: str = None,
		end: str = None,
		description=None,
		location=None,
		class_role: str = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		# get a list of upcoming events
		events = self.calendar_service.fetch_upcoming(calendar.id, query)
		# no events found
		if len(events) == 0:
			raise FriendlyError(
				f"No events were found for '{query}'.", ctx.channel, ctx.author
			)
		# multiple events found
		elif len(events) > 1:
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
			await ctx.send(embed=embed)
			# ask user to pick an event with emojis
			selection_index = await wait_for_reaction(
				bot=self.bot,
				message=ctx.message,
				emoji_list=self.number_emoji[: len(events)],
				allowed_users=[ctx.author],
			)
			# get the event selected by the user
			event_to_update = events[selection_index]
		# only 1 event found
		else:
			# get the event at index 0
			event_to_update = events[0]
		# replace channel mentions
		if title is not None:
			self.course_mentions.replace_channel_mentions(title)
		if description is not None:
			self.course_mentions.replace_channel_mentions(description)
		if location is not None:
			self.course_mentions.replace_channel_mentions(location)
		try:
			event = self.calendar_service.update_event(
				calendar.id, event_to_update, title, start, end, description, location
			)
		except ValueError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
			":white_check_mark: Event updated successfully", event
		)
		# edit message if sent already, otherwise send
		sender = ctx.send if ctx.message is None else ctx.message.edit
		await sender(embed=embed)

	@cog_ext.cog_subcommand(
		base="events",
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
				# option returns class role and calendar as value
				name="class_role",
				description=(
					"Calendar to look for events in (eg. Lev 2023). Only necessary if"
					" you have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def event_delete(
		self, ctx: SlashContext, query: str, class_role: str = None,
	):
		await ctx.defer()
		# replace channel mentions with course names
		query = self.course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		# fetch upcoming events
		events = self.calendar_service.fetch_upcoming(calendar.id, query)
		# no events found
		if len(events) == 0:
			raise FriendlyError(f"No events were found for '{query}'.", ctx, ctx.author)
		# multiple events found
		elif len(events) > 1:
			embed = self.calendar_embedder.embed_event_list(
				title=f"⚠ Multiple events were found.",
				events=events,
				description=(
					"Please specify which event you would like to delete."
					f'\n\nShowing results for "{query}"'
				),
				colour=discord.Colour.gold(),
				enumeration=self.number_emoji,
			)
			await ctx.send(embed=embed)
			# ask user to pick an event with emojis
			selection_index = await wait_for_reaction(
				bot=self.bot,
				message=ctx.message,
				emoji_list=self.number_emoji[: len(events)],
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
			raise FriendlyError(error.args[0], ctx, ctx.author, error)
		embed = self.calendar_embedder.embed_event(
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
				# option returns class role and calendar as value
				name="class_role",
				description=(
					"Calendar to look for events in (eg. Lev 2023). Only necessary if"
					" you have more than one class role."
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					create_choice(
						name=class_role.name,
						value=f"{class_role.name} {class_role.calendar}",
					)
					for class_role in ClassRole.get_class_roles()
				],
			),
		],
	)
	async def calendar_grant(
		self, ctx: SlashContext, email: str, class_role: str = None,
	):
		await ctx.defer()
		# get calendar from selected class_role or author
		calendar = self.finder.get_calendar(ctx, class_role)
		# validate email address
		if not is_email(email):
			raise FriendlyError("Invalid email address", ctx.channel, ctx.author)
		# add manager to calendar
		if self.calendar_service.add_manager(calendar.id, email):
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
		self.calendar_creator.create_class_calendars(year)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))
