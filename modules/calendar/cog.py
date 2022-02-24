import nextcord
import nextcord
import config
from nextcord import SlashOption
from nextcord.ext import commands
from .calendar import Calendar
from .calendar_service import CalendarService
from .calendar_embedder import CalendarEmbedder
from .calendar_creator import CalendarCreator
from . import course_mentions
from ..error.friendly_error import FriendlyError
from utils.embedder import embed_success
from utils.utils import is_email
from database.group import Group
from database import preloaded


class CalendarCog(commands.Cog):
	"""Display and update Google Calendar events"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		timezone = "Asia/Jerusalem"
		self.embedder = CalendarEmbedder(bot, timezone)
		self.service = CalendarService(timezone)
		self.creator = CalendarCreator(self.service)

	@nextcord.slash_command(description="Calendar group", guild_ids=[config.guild_id])
	async def calendar(self, interaction: nextcord.Interaction):
		"""This is a base command for all calendar commands and is not invoked"""
		pass

	@calendar.subcommand(
		name="links",
		description="Get the links to add or view the calendar",
	)
	async def calendar_links(
		self,
		interaction: nextcord.Interaction,
		group_id: int = SlashOption(
			name="class_name",
			description="Calendar to show links for (eg. Lev 2023). Leave blank if you have only one class role.",
			required=False,
			choices={group.name: group.id for group in preloaded.groups},
		),
	):
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		# fetch links for calendar
		links = self.service.get_links(calendar)
		embed = self.embedder.embed_links(
			f"🔗 Calendar Links for {calendar.name}", links
		)
		await interaction.send(embed=embed)

	@calendar.subcommand(
		name="events",
		description="Display upcoming events from the Google Calendar",
	)
	async def events(
		self,
		interaction: nextcord.Interaction,
		query: str = SlashOption(
			description="Query or channel mention to search for within event titles (if not specified, shows all events)",
			required=False,
			default="",
		),
		results_per_page: int = SlashOption(
			description="Number of events to display per page. (Default: 5)",
			required=False,
			default=5,
		),
		group_id: int = SlashOption(
			name="class_name",
			description=(
				"Calendar to show events for (eg. Lev 2023). Leave blank if you have only one class role."
			),
			required=False,
			choices={group.name: group.id for group in preloaded.groups},
		),
	):
		await interaction.response.defer()
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		# convert channel mentions to full names
		full_query = await course_mentions.replace_channel_mentions(query)
		# fetch upcoming events
		events = self.service.fetch_upcoming(calendar.id, full_query)
		# display events and allow showing more with reactions
		await self.embedder.embed_event_pages(
			interaction, events, full_query, results_per_page, calendar
		)

	@calendar.subcommand(name="add", description="Add events to the Google Calendar")
	async def event_add(
		self,
		interaction: nextcord.Interaction,
		title: str = SlashOption(
			description='Title of the event (eg. "HW 1 #statistics")'
		),
		start: str = SlashOption(
			description='The start date of the event in Israel Time (eg. "April 15, 2pm")'
		),
		end: str = SlashOption(
			description='The end date of the event in Israel Time (eg. "3pm")',
			required=False,
		),
		description: str = SlashOption(
			description='The description of the event (eg. "Submission box: https://moodle.jct.ac.il/123")',
			required=False,
			default="",
		),
		location: str = SlashOption(
			description='The location of the event (eg. "Brause 305")',
			required=False,
			default="",
		),
		group_id: int = SlashOption(
			name="class_name",
			description=(
				"Calendar to add event to (eg. Lev 2023). Leave blank if you"
				" have only one class role."
			),
			choices={group.name: group.id for group in preloaded.groups},
			required=False,
		),
	):
		await interaction.response.defer()
		# replace channel mentions with course names
		title = await course_mentions.replace_channel_mentions(title)
		description = await course_mentions.replace_channel_mentions(description)
		location = await course_mentions.replace_channel_mentions(location)
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		try:
			event = self.service.add_event(
				calendar.id, title, start, end, description, location
			)
		except ValueError as error:
			raise FriendlyError(str(error), interaction, interaction.user, error)
		embed = self.embedder.embed_event(
			f":white_check_mark: Event added to {calendar.name} calendar successfully",
			event,
			calendar,
		)
		await interaction.send(embed=embed)

	@calendar.subcommand(
		name="update",
		description="Update events in the Google Calendar",
	)
	async def event_update(
		self,
		interaction: nextcord.Interaction,
		query: str = SlashOption(
			description="Query or channel mention to search for within event titles"
		),
		title: str = SlashOption(
			description='New title of the event (eg. "HW 1 #statistics"). ${title} refers to old title.',
			required=False,
		),
		start: str = SlashOption(
			description='New start date of the event in Israel Time (eg. "April 15, 2pm")',
			required=False,
		),
		end: str = SlashOption(
			description='New end date of the event in Israel Time (eg. "3pm")',
			required=False,
		),
		description: str = SlashOption(
			description='eg. "[Submission](https://...)". ${description} refers to old  description. Use \\n for newlines.")',
			required=False,
		),
		location: str = SlashOption(
			description='The location of the event (eg. "Brause 305"). ${location} refers to old location.',
			required=False,
		),
		group_id: int = SlashOption(
			name="class_name",
			description=(
				"Calendar to update event in (eg. Lev 2023). Leave blank if you"
				" have only one class role."
			),
			choices={group.name: group.id for group in preloaded.groups},
			required=False,
		),
	):
		await interaction.response.defer()
		# replace channel mentions with course names
		query = await course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		# get a list of upcoming events
		events = self.service.fetch_upcoming(calendar.id, query)
		# get event to update
		event_to_update = await self.embedder.get_event_choice(
			interaction, events, calendar, query, "update"
		)
		# replace channel mentions and variables
		if title:
			title = (await course_mentions.replace_channel_mentions(title)).replace(
				"${title}", event_to_update.title
			)
		if description:
			description = (
				(await course_mentions.replace_channel_mentions(description))
				.replace("${description}", event_to_update.description or "")
				.replace("\\n", "\n")
			)
		if location:
			location = (
				await course_mentions.replace_channel_mentions(location)
			).replace("${location}", event_to_update.location or "")
		try:
			event = self.service.update_event(
				calendar.id,
				event_to_update,
				title,
				start,
				end,
				description,
				location,
			)
		except ValueError as error:
			raise FriendlyError(error.args[0], interaction, interaction.user, error)
		embed = self.embedder.embed_event(
			":white_check_mark: Event updated successfully", event, calendar
		)
		# edit message if sent already, otherwise send
		sender = (
			interaction.send
			if not interaction.response.is_done()
			else interaction.edit_original_message
		)
		await sender(embed=embed)

	@calendar.subcommand(
		name="delete",
		description="Delete events from the Google Calendar",
	)
	async def event_delete(
		self,
		interaction: nextcord.Interaction,
		query: str = SlashOption(
			description="Query or channel mention to search for within event titles"
		),
		group_id: int = SlashOption(
			name="class_name",
			description=(
				"Calendar to delete event from (eg. Lev 2023). Leave blank if you"
				" have only one class role."
			),
			choices={group.name: group.id for group in preloaded.groups},
			required=False,
		),
	):
		await interaction.response.defer()
		# replace channel mentions with course names
		query = await course_mentions.replace_channel_mentions(query)
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		# fetch upcoming events
		events = self.service.fetch_upcoming(calendar.id, query)
		# get event to delete
		event_to_delete = await self.embedder.get_event_choice(
			interaction, events, calendar, query, "delete"
		)
		# delete event
		try:
			self.service.delete_event(calendar.id, event_to_delete)
		except ConnectionError as error:
			raise FriendlyError(error.args[0], interaction, interaction.user, error)
		embed = self.embedder.embed_event(
			"🗑 Event deleted successfully", event_to_delete, calendar
		)
		# edit message if sent already, otherwise send
		sender = (
			interaction.send
			if not interaction.response.is_done()
			else interaction.edit_original_message
		)
		await sender(embed=embed)

	@calendar.subcommand(
		name="grant",
		description="Add a Google account as a manager of your class's calendar",
	)
	async def calendar_grant(
		self,
		interaction: nextcord.Interaction,
		email: str = SlashOption(
			description="The email address of the Google account to add",
		),
		group_id: int = SlashOption(
			name="class_name",
			description=(
				"Calendar to get access to (eg. Lev 2023). Leave blank if you"
				" have only one class role."
			),
			choices={group.name: group.id for group in preloaded.groups},
			required=False,
		),
	):
		await interaction.response.defer(hidden=True)
		# get calendar from selected class_role or author
		calendar = await Calendar.get_calendar(
			interaction, await Group.get_groups(), group_id
		)
		# validate email address
		if not is_email(email):
			raise FriendlyError(
				"Invalid email address", interaction, interaction.user, hidden=True
			)
		# add manager to calendar
		if self.service.add_manager(calendar.id, email):
			embed = embed_success(
				f":office_worker: Successfully added manager to {calendar.name}."
			)
			await interaction.send(embed=embed, hidden=True)
			return
		raise FriendlyError(
			"An error occurred while applying changes.",
			interaction,
			interaction.user,
			hidden=True,
		)


# setup functions for bot
def setup(bot):
	bot.add_cog(CalendarCog(bot))
