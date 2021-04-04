from utils.utils import get_discord_obj
from database.group.group import Group
from typing import Iterable
from utils.sql_fetcher import SqlFetcher
from datetime import datetime
import psycopg2.extensions as sql
import discord


class Graduator:
	def __init__(
		self, conn: sql.connection, sql_fetcher: SqlFetcher, guild: discord.Guild
	):
		self.conn = conn
		self.sql_fetcher = sql_fetcher
		self.guild = guild

	def get_graduating_groups(self) -> Iterable[Group]:
		"""Get the channel IDs of the graduating groups."""
		return [
			group
			for group in Group.get_groups()
			if group.grad_year == datetime.now().year
		]

	async def add_alumni_role(self, groups: Iterable[Group]):
		"""Add the alumni role to all members of the given groups only if they have no other group roles"""
		alumni_role = get_discord_obj(self.guild().roles, "ALUMNI_ROLE")
		group_roles = {group.role() for group in Group.get_groups()}
		for group in groups:
			for member in group.role().members:
				if len(group_roles.intersection(member.roles)) == 1:
					await member.add_roles(alumni_role)