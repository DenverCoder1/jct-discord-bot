from database.campus.campus import Campus
import discord
import config
from typing import Iterable
from functools import cache
from database import sql_fetcher


class Group:
	def __init__(
		self, id: int, grad_year: int, campus_id: int, role_id: int, calendar: str
	):
		self.id = id
		self.grad_year = grad_year
		self.campus_id = campus_id
		self.role_id = role_id
		self.calendar = calendar
		self.name = f"{self.campus().name} {self.grad_year}"

	@cache
	def role(self) -> discord.Role:
		return discord.utils.get(config.guild().roles, id=self.role_id)

	@cache
	def campus(self) -> Campus:
		return Campus.get_campus(self.campus_id)

	@staticmethod
	def get_group(group_id: int) -> "Group":
		"""Fetch a group from the database given its ID."""
		query = sql_fetcher.fetch("database", "group", "queries", "get_group.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"group_id": group_id})
				return Group(*cursor.fetchone())

	@staticmethod
	def get_groups() -> Iterable["Group"]:
		"""Fetch a list of groups from the database"""
		query = sql_fetcher.fetch("database", "group", "queries", "get_groups.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [Group(*tup) for tup in cursor.fetchall()]