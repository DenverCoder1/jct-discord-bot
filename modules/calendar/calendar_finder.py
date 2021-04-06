from utils.utils import one
from database.group.group import Group
from discord_slash.context import SlashContext
from modules.error.friendly_error import FriendlyError
from .calendar import Calendar
import discord
from typing import Iterable, Optional
from .group_role_error import GroupRoleError


def get_calendar(
	ctx: SlashContext,
	groups: Optional[Iterable[Group]] = None,
	group_id: Optional[int] = None,
) -> Calendar:
	"""Returns the Calendar of the given group_id"""
	if group_id is not None:
		groups = groups or Group.get_groups()
		group = one(groups, lambda group: group.group_id == group_id)
		return Calendar(name=group.name, id=group.calendar)
	# get calendar from user's role
	else:
		try:
			return __get_calendar_from_role(ctx.author)
		except GroupRoleError as error:
			raise FriendlyError(error.args[0], ctx, ctx.author, error)


def __get_calendar_from_role(member: discord.Member) -> Calendar:
	# get grad_year and campus for member
	group = __get_group_from_role(member)
	# get and return calendar info
	return Calendar(id=group.calendar, name=group.name)


def __get_group_from_role(member: discord.Member) -> Group:
	"""Returns the Group for a member who is only in one Group"""
	groups = Group.get_member_groups(member)
	if len(groups) > 1:
		raise GroupRoleError(
			"You must specify which calendar since you have multiple class roles."
		)
	elif len(groups) == 0:
		raise GroupRoleError("Could not find your class role.")
	return one(groups)
