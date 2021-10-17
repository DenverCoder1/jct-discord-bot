from database.group import Group
import discord
import psycopg2.extensions as sql
from database import sql_fetcher
from database.campus import Campus
from . import group_channel_creator
import config


class NewGroup:
	def __init__(self, campus: Campus, year: int, conn: sql.connection):
		self.__campus = campus
		self.__year = year
		self.__conn = conn
		self.__role: discord.Role
		self.__channel: discord.TextChannel

	@property
	def campus(self) -> Campus:
		"""The campus that this new group belongs to."""
		return self.__campus

	@property
	def year(self) -> int:
		"""The new group's graduation year'."""
		return self.__year

	@property
	def role(self) -> discord.Role:
		"""The new group's newly created role."""
		if not self.__role:
			raise AttributeError()
		return self.__role

	@property
	def channel(self) -> discord.TextChannel:
		"""The new group's newly created role."""
		if not self.__channel:
			raise AttributeError()
		return self.__channel

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
		return colours[self.__year % len(colours)]

	async def __create_role(self):
		self.__role = await config.guild().create_role(
			name=f"{self.__campus.name} {self.__year}",
			permissions=discord.Permissions.none(),
			colour=self.__get_colour(),
			hoist=True,
			mentionable=True,
		)

	async def __move_role(self):
		roles = [group.role for group in Group.get_groups()]
		positions = [role.position for role in roles]
		new_position = min(positions) - 1
		position_dict = {self.role: new_position}
		await config.guild().edit_role_positions(position_dict)

	async def __create_group_channel(self):
		self.__channel = await group_channel_creator.create_group_channel(
			f"📚︱{self.__year}-{self.__campus.name.lower()}",
			[self.__role],
			"Here you can discuss schedules, links, and courses your class is taking.",
		)

	async def __add_to_campus_channel(self):
		self.__campus.channel.set_permissions(
			target=self.__role, view_channel=True,
		)

	def __add_to_database(self):
		query = sql_fetcher.fetch("modules", "create_group", "queries", "add_group.sql")
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query,
					{
						"year": self.__year,
						"campus_id": self.__campus.id,
						"role_id": self.__role.id,
					},
				)
