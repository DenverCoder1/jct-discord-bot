"""
This module is supposed to contain all the data from the database that would be
required from places where async calls are not allowed.

If you need to access some data from the database for example in a function
decorator, you can declare it in this file, assign it asynchronously in the
__load() function, then import it wherever you need it.

Just make sure you call await load() sometime before you use any of the data in
this module.
"""


from typing import Collection

from database.campus import Campus
from .group import Group

groups: Collection[Group] = []
campuses: Collection[Campus] = []


async def load():
	global groups, campuses
	groups = await Group.get_groups()
	campuses = await Campus.get_campuses()