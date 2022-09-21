from typing import Optional

import nextcord
from nextcord.ext import commands

import config
from database import preloaded
from database.group import Group
from utils.embedder import embed_success
from utils.utils import is_email

from ..error.friendly_error import FriendlyError
from . import course_mentions
from .calendar import Calendar
from .calendar_creator import CalendarCreator
from .calendar_embedder import CalendarEmbedder
from .calendar_service import CalendarService


class CalendarCog(commands.Cog):
    """Display and update Google Calendar events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        timezone = "Asia/Jerusalem"
        self.embedder = CalendarEmbedder(bot, timezone)
        self.service = CalendarService(timezone)
        self.creator = CalendarCreator(self.service)

    @nextcord.slash_command(guild_ids=[config.guild_id])
    async def calendar(self, interaction: nextcord.Interaction[commands.Bot]):
        """This is a base command for all calendar commands and is not invoked"""
        pass

    @calendar.subcommand(name="links")
    async def calendar_links(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Get the links to add or view the calendar

        Args:
            group_id: Calendar to show links for (eg. Lev 2023). Leave blank if you have only one class role.
        """
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(interaction, await Group.get_groups(), group_id)
        # fetch links for calendar
        links = self.service.get_links(calendar)
        embed = self.embedder.embed_links(f"🔗 Calendar Links for {calendar.name}", links)
        await interaction.send(embed=embed)

    @calendar.subcommand(name="events")
    async def events(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        query: str = "",
        results_per_page: int = 5,
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Display upcoming events from the Google Calendar

        Args:
            query: Query or channel mention to search for within event titles (if not specified,
                shows all events)
            results_per_page: Number of events to display per page. (Default: 5)
            group_id: Calendar to show events for (eg. Lev 2023). Leave blank if you have only one
                class role.
        """
        await interaction.response.defer()
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(interaction, await Group.get_groups(), group_id)
        # convert channel mentions to full names
        full_query = await course_mentions.replace_channel_mentions(query)
        # fetch upcoming events
        events = self.service.fetch_upcoming(calendar.id, full_query)
        # display events and allow showing more with reactions
        await self.embedder.embed_event_pages(
            interaction, events, full_query, results_per_page, calendar
        )

    @calendar.subcommand(name="add")
    async def event_add(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        title: str,
        start: str,
        end: Optional[str] = None,
        description: str = "",
        location: str = "",
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Add an event to the Google Calendar

        Args:
            title: Title of the event (eg. "HW 1 #statistics")
            start: The start date of the event in Israel Time (eg. "April 15, 2pm")
            end: The end date of the event in Israel Time (eg. "3pm")
            description: The description of the event (eg. "Submission box: https://moodle.jct.ac.il/123")
            location: The location of the event (eg. "Brause 305")
            group_id: Calendar to add event to (eg. Lev 2023). Leave blank if you have only one class role.
        """
        await interaction.response.defer()
        # replace channel mentions with course names
        title = await course_mentions.replace_channel_mentions(title)
        description = await course_mentions.replace_channel_mentions(description)
        location = await course_mentions.replace_channel_mentions(location)
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(interaction, await Group.get_groups(), group_id)
        try:
            event = self.service.add_event(calendar.id, title, start, end, description, location)
        except ValueError as error:
            raise FriendlyError(str(error), interaction, interaction.user, error)
        embed = self.embedder.embed_event(
            f":white_check_mark: Event added to {calendar.name} calendar successfully",
            event,
            calendar,
        )
        await interaction.send(embed=embed)

    @calendar.subcommand(name="update")
    async def event_update(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        query: str,
        title: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Update an event in the Google Calendar

        Args:
            query: Query or channel mention to search for within event titles
            title: New title of the event (eg. "HW 1 #statistics"). ${title} refers to old title.
            start: New start date of the event in Israel Time (eg. "April 15, 2pm")
            end: New end date of the event in Israel Time (eg. "3pm")
            description: eg. "[Submission](https://...)". ${description} refers to old description. Use
                \\n for newlines.")
            location: New location of the event (eg. "Brause 305"). ${location} refers to old location.
            group_id: Calendar to update event in (eg. Lev 2023). Leave blank if you have only one class role.
        """
        await interaction.response.defer()
        # replace channel mentions with course names
        query = await course_mentions.replace_channel_mentions(query)
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(interaction, await Group.get_groups(), group_id)
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
            location = (await course_mentions.replace_channel_mentions(location)).replace(
                "${location}", event_to_update.location or ""
            )
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
        await interaction.edit_original_message(embed=embed)

    @calendar.subcommand(name="delete")
    async def event_delete(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        query: str,
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Delete an event from the Google Calendar

        Args:
            query: Query or channel mention to search for within event titles
            group_id: Calendar to delete event from (eg. Lev 2023). Leave blank if you have only one class role.
        """
        await interaction.response.defer()
        # replace channel mentions with course names
        query = await course_mentions.replace_channel_mentions(query)
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(interaction, await Group.get_groups(), group_id)
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
        embed = self.embedder.embed_event("🗑 Event deleted successfully", event_to_delete, calendar)
        # edit message if sent already, otherwise send
        await interaction.edit_original_message(embed=embed)

    @calendar.subcommand(name="grant")
    async def calendar_grant(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        email: str,
        group_id: Optional[int] = nextcord.SlashOption(
            name="class_name",
            choices={group.name: group.id for group in preloaded.groups},
        ),
    ):
        """Add a Google account as a manager of your class's calendar

        Args:
            email: The email address of the Google account to add
            group_id: Calendar to get access to (eg. Lev 2023). Leave blank if you have only one class role.
        """
        await interaction.response.defer(ephemeral=True)
        # get calendar from selected class_role or author
        calendar = await Calendar.get_calendar(
            interaction,
            await Group.get_groups(),
            group_id,
            ephemeral=True,
        )
        # validate email address
        if not is_email(email):
            raise FriendlyError(
                "Invalid email address",
                interaction,
                interaction.user,
                ephemeral=True,
            )
        # add manager to calendar
        if self.service.add_manager(calendar.id, email):
            embed = embed_success(f":office_worker: Successfully added manager to {calendar.name}.")
            await interaction.send(embed=embed, ephemeral=True)
            return
        raise FriendlyError(
            "An error occurred while applying changes.",
            interaction,
            interaction.user,
            ephemeral=True,
        )


# setup functions for bot
def setup(bot):
    bot.add_cog(CalendarCog(bot))
