from database.campus.campus import Campus
import discord
import config
from typing import Collection
from functools import cached_property
from database import sql_fetcher


class Group:
	def __init__(
		self, id: int, grad_year: int, campus_id: int, role_id: int, calendar: str
	):
		self.__id = id
		self.__grad_year = grad_year
		self.__campus_id = campus_id
		self.__role_id = role_id
		self.__calendar = calendar

	@property
	def id(self) -> int:
		"""The ID of the group as stored in the database."""
		return self.__id

	@property
	def grad_year(self) -> int:
		"""The year in which this group is to graduate."""
		return self.__grad_year

	@cached_property
	def campus(self) -> Campus:
		"""The campus this Group belongs to"""
		return Campus.get_campus(self.__campus_id)

	@cached_property
	def role(self) -> discord.Role:
		"""The Role associated with this Group."""
		return discord.utils.get(config.guild().roles, id=self.__role_id)

	@property
	def calendar(self) -> str:
		"""The calendar id associated with this Group. (Looks like an email address)"""
		return self.__calendar

	@property
	def name(self) -> str:
		"""The name of this Group. (eg Lev 2021)"""
		return f"{self.campus.name} {self.__grad_year}"

	@classmethod
	def get_group(cls, group_id: int) -> "Group":
		"""Fetch a group from the database given its ID."""
		query = sql_fetcher.fetch("database", "group", "queries", "get_group.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"group_id": group_id})
				return cls(*cursor.fetchone())

	@classmethod
	def get_groups(cls) -> Collection["Group"]:
		"""Fetch a list of groups from the database"""
		query = sql_fetcher.fetch("database", "group", "queries", "get_groups.sql")
		with config.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query)
				return [cls(*tup) for tup in cursor.fetchall()]

	def __eq__(self, other):
		"""Compares them by ID"""
		if isinstance(other, self.__class__):
			return self.__id == other.__id
		return False

	def __hash__(self):
		return hash(self.__id)