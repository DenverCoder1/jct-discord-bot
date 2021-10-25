from database.campus import Campus
import discord
import config
from typing import Collection
from functools import cached_property
from database import sql
from async_lru import alru_cache as async_cache


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

	@async_cache
	async def campus(self) -> Campus:
		"""The campus this Group belongs to"""
		return await Campus.get_campus(self.__campus_id)

	@cached_property
	def role(self) -> discord.Role:
		"""The Role associated with this Group."""
		role = discord.utils.get(config.guild().roles, id=self.__role_id)
		assert role is not None
		return role

	@property
	def calendar(self) -> str:
		"""The calendar id associated with this Group. (Looks like an email address)"""
		return self.__calendar

	@async_cache
	async def name(self) -> str:
		"""The name of this Group. (eg Lev 2021)"""
		return f"{(await self.campus()).name} {self.__grad_year}"

	@classmethod
	async def get_group(cls, group_id: int) -> "Group":
		"""Fetch a group from the database given its ID."""
		record = await sql.select.one(
			"groups", ("id", "grad_year", "campus", "role", "calendar"), id=group_id
		)
		assert record is not None
		return cls(*record)

	@classmethod
	async def get_groups(cls) -> Collection["Group"]:
		"""Fetch a list of groups from the database"""
		records = await sql.select.many(
			"groups", ("id", "grad_year", "campus", "role", "calendar")
		)
		return [cls(*record) for record in records]

	def __eq__(self, other):
		"""Compares them by ID"""
		if isinstance(other, self.__class__):
			return self.__id == other.__id
		return False

	def __hash__(self):
		return hash(self.__id)