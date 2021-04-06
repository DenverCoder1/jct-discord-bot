from database.group.group import Group
import discord
import psycopg2.extensions as sql
from database import sql_fetcher
from database.campus.campus import Campus
from .group_channel_creator import GroupChannelCreator
import config


class NewGroup:
	def __init__(self, campus: Campus, year: int, conn: sql.connection):
		self.campus = campus
		self.year = year
		self.__conn = conn
		self.role = None
		self.channel = None

	async def add_to_system(self):
		await self.__create_role()
		await self.__move_role()
		await self.__create_group_channel()
		await self.__add_to_campus_channel()
		self.__add_to_database()

	def __get_colour(self) -> discord.Colour:
		colours = [
			discord.Colour.from_rgb(255, 77, 149),
			discord.Colour.from_rgb(235, 154, 149),
			discord.Colour.from_rgb(75, 147, 213),
			discord.Colour.from_rgb(110, 213, 144),
		]
		return colours[self.year % len(colours)]

	async def __create_role(self):
		self.role = await config.guild().create_role(
			name=f"{self.campus.name} {self.year}",
			permissions=discord.Permissions.none(),
			colour=self.__get_colour(),
			hoist=True,
			mentionable=True,
		)

	async def __move_role(self):
		roles = [group.role() for group in Group.get_groups()]
		positions = [config.guild().get_role(role).position for role in roles]
		new_position = min(positions) - 1
		positions = {self.role: new_position}
		await config.guild().edit_role_positions(positions)

	async def __create_group_channel(self):
		self.channel = await GroupChannelCreator.create_group_channel(
			f"📚{self.year}-{self.campus.name.lower()}", [self.role]
		)

	async def __add_to_campus_channel(self):
		self.campus.channel().set_permissions(
			target=self.role, view_channel=True,
		)

	def __add_to_database(self):
		query = sql_fetcher.fetch("modules", "create_group", "queries", "add_group.sql")
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query,
					{
						"year": self.year,
						"campus_id": self.campus.campus_id,
						"role_id": self.role.id,
					},
				)
