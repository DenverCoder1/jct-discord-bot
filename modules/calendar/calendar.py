from modules.error.friendly_error import FriendlyError
from utils.utils import one
from database.group.group import Group
from typing import Dict, Iterable
from discord_slash.context import SlashContext


class Calendar:
	"""Calendar object to store information about a Google Calendar"""

	def __init__(self, id: str, name: str):
		"""Create a calendar object from a calendar id and name"""
		self.__id = id
		self.__name = name

	@property
	def id(self) -> int:
		"""The ID of the Google calendar"""
		return self.__id

	@property
	def name(self) -> str:
		"""The name of the calendar"""
		return self.__name

	@classmethod
	def from_dict(cls, details: Dict[str, str]) -> "Calendar":
		"""Create a calendar from a JSON object as returned by the Calendar API"""
		return cls(id=details.get("id"), name=details.get("summary"))

	@staticmethod
	def get_calendar(
		ctx: SlashContext, groups: Iterable[Group], group_id: int = None
	) -> "Calendar":
		"""Returns Calendar given a Discord member or a specified group id"""
		if group_id is not None:
			# get the group specified by the user given the group id
			group = one(groups, lambda group: group.group_id == group_id)
		else:
			# get the group from the user's role
			group_roles = [group for group in groups if group.role in ctx.author.roles]
			# no group roles found
			if not group_roles:
				raise FriendlyError(
					"Could not find your class role.", ctx, ctx.author,
				)
			# multiple group roles found
			if len(group_roles) > 1:
				raise FriendlyError(
					"You must specify which calendar since you have multiple class"
					" roles.",
					ctx,
					ctx.author,
				)
			# only one group found
			group = group_roles[0]
		# return calendar for the group
		return Calendar(id=group.calendar, name=group.name)
