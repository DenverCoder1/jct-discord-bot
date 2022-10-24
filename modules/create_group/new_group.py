import nextcord

import config
from database import sql
from database.campus import Campus
from database.group import Group
from modules.calendar.calendar import Calendar

from . import group_channel_creator


class NewGroup:
    def __init__(self, campus: Campus, year: int, calendar: Calendar):
        self.__campus = campus
        self.__year = year
        self.__calendar = calendar
        self.__role: nextcord.Role
        self.__channel: nextcord.TextChannel

    @property
    def campus(self) -> Campus:
        """The campus that this new group belongs to."""
        return self.__campus

    @property
    def year(self) -> int:
        """The new group's graduation year'."""
        return self.__year

    @property
    def role(self) -> nextcord.Role:
        """The new group's newly created role."""
        if not self.__role:
            raise AttributeError()
        return self.__role

    @property
    def channel(self) -> nextcord.TextChannel:
        """The new group's newly created role."""
        if not self.__channel:
            raise AttributeError()
        return self.__channel

    @property
    def calendar(self) -> Calendar:
        """The new group's calendar."""
        return self.__calendar

    async def add_to_system(self):
        await self.__create_role()
        await self.__move_role()
        await self.__create_group_channel()
        await self.__add_to_campus_channel()
        await self.__add_to_database()

    def __get_colour(self) -> nextcord.Colour:
        colours = [
            nextcord.Colour.from_rgb(255, 77, 149),
            nextcord.Colour.from_rgb(235, 154, 149),
            nextcord.Colour.from_rgb(75, 147, 213),
            nextcord.Colour.from_rgb(110, 213, 144),
        ]
        return colours[self.__year % len(colours)]

    async def __create_role(self):
        self.__role = await config.guild().create_role(
            name=f"{self.__campus.name} {self.__year}",
            permissions=nextcord.Permissions.none(),
            colour=self.__get_colour(),
            hoist=True,
            mentionable=True,
        )

    async def __move_role(self):
        roles = [group.role for group in await Group.get_groups()]
        positions = [role.position for role in roles]
        new_position = min(positions) - 1
        position_dict = {self.role: new_position}
        await config.guild().edit_role_positions(position_dict)  # type: ignore

    async def __create_group_channel(self):
        self.__channel = await group_channel_creator.create_group_channel(
            f"📚︱{self.__year}-{self.__campus.name.lower()}",
            [self.__role],
            "Here you can discuss schedules, links, and courses your class is taking.",
        )

    async def __add_to_campus_channel(self):
        await self.__campus.channel.set_permissions(
            target=self.__role,
            view_channel=True,
        )

    async def __add_to_database(self):
        await sql.insert(
            "groups",
            grad_year=self.year,
            campus=self.campus.id,
            role=self.role.id,
            calendar=self.calendar.id,
        )
