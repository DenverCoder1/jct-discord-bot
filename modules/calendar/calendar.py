from modules.error.friendly_error import FriendlyError
from utils.utils import one
from database.group import Group
from typing import Dict, Iterable, Optional
import nextcord


class Calendar:
	"""Calendar object to store information about a Google Calendar"""

	def __init__(self, id: str, name: str):
		"""Create a calendar object from a calendar id and name"""
		self.__id = id
		self.__name = name

	@property
	def id(self) -> str:
		"""The ID of the Google calendar"""
		return self.__id

	@property
	def name(self) -> str:
		"""The name of the calendar"""
		return self.__name

	def add_url(self) -> str:
		"""The url to add the calendar to Google Calendar"""
		return (
			"https://calendar.google.com/calendar/render"
			f"?cid=https://www.google.com/calendar/feeds/{self.__id}"
			"/public/basic"
		)

	def view_url(self, timezone: str) -> str:
		"""The url to view the calendar"""
		return (
			"https://calendar.google.com/calendar/u/0/embed"
			f"?src={self.__id}&ctz={timezone}"
		)

	def ical_url(self) -> str:
		"""The iCal url for the calendar"""
		return (
			"https://calendar.google.com/calendar/ical"
			f"/{self.__id.replace('@','%40')}/public/basic.ics"
		)

	@classmethod
	def from_dict(cls, details: Dict[str, str]) -> "Calendar":
		"""Create a calendar from a JSON object as returned by the Calendar API"""
		return cls(id=details["id"], name=details["summary"])

	@classmethod
	async def get_calendar(
		cls,
		interaction: nextcord.Interaction,
		groups: Optional[Iterable[Group]] = None,
		group_id: Optional[int] = None,
	) -> "Calendar":
		"""Returns Calendar given a Discord member or a specified group id"""
		groups = groups or await Group.get_groups()
		if group_id:
			# get the group specified by the user given the group id
			group = one(group for group in groups if group.id == group_id)
		else:
			# get the group from the user's role
			member_groups = [
				group for group in groups if group.role in interaction.user.roles
			]
			# no group roles found
			if not member_groups:
				raise FriendlyError(
					"Could not find your class role.",
					interaction,
					interaction.user,
					hidden=True,
				)
			# multiple group roles found
			if len(member_groups) > 1:
				raise FriendlyError(
					"You must specify which calendar since you have multiple class"
					" roles.",
					interaction,
					interaction.user,
					hidden=True,
				)
			# only one group found
			group = one(member_groups)
		# return calendar for the group
		return cls(id=group.calendar, name=group.name)
