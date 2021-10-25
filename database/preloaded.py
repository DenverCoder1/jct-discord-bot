from typing import Collection
from .group import Group

groups: Collection[Group] = []


async def load():
	global groups
	groups = await Group.get_groups()
