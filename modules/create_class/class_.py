import discord
from utils.utils import get_discord_obj
import psycopg2.extensions as sql
from utils.sql_fetcher import SqlFetcher
from utils.campus.campus import Campus
from .class_channel_creator import ClassChannelCreator
import config


class Class:
	def __init__(
		self, campus: Campus, year: int, conn: sql.connection, sql_fetcher: SqlFetcher,
	):
		self.campus = campus
		self.year = year
		self.__conn = conn
		self.__sql_fetcher = sql_fetcher
		self.role = None
		self.channel = None

	async def add_to_system(self):
		await self.__create_role()
		await self.__move_role()
		await self.__create_class_channel()
		self.__add_to_database()

	def __get_colour(self) -> discord.Colour:
		colours = [
			discord.Colour.from_rgb(255, 77, 149),
			discord.Colour.from_rgb(235, 154, 149),
			discord.Colour.from_rgb(75, 147, 213),
			discord.Colour.from_rgb(110, 213, 144),
		]
		return colours[self.year % len(colours)]

	async def __create_role(self) -> discord.Role:
		self.role = await config.guild.create_role(
			name=f"{self.campus.name} {self.year}",
			permissions=discord.Permissions.none(),
			colour=self.__get_colour(),
			hoist=True,
			mentionable=True,
		)

	async def __move_role(self):
		query = self.__sql_fetcher.fetch(
			"modules", "create_class", "queries", "get_roles.sql"
		)
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				roles = [row[0] for row in cursor.fetchall()]
		positions = [config.guild.get_role(role).position for role in roles]
		new_position = min(positions) - 1
		positions = {self.role: new_position}
		await config.guild.edit_role_positions(positions)

	async def __create_class_channel(self):
		self.channel = await ClassChannelCreator.create_class_channel(
			f"📚{self.year}-{self.campus.name.lower()}", [self]
		)

	def __add_to_database(self):
		query = self.__sql_fetcher.fetch(
			"modules", "create_class", "queries", "add_class.sql"
		)
		with self.__conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(
					query,
					{
						"year": self.year,
						"campus_id": self.campus.id,
						"role_id": self.role.id,
					},
				)
