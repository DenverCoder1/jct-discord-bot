from datetime import datetime
from typing import Iterable

import config
from database.group import Group
from utils.utils import get_discord_obj


async def get_graduating_groups() -> Iterable[Group]:
    """Get the channel IDs of the graduating groups."""
    return [group for group in await Group.get_groups() if group.grad_year == datetime.now().year]


async def add_alumni_role(groups: Iterable[Group]):
    """Add the alumni role to all members of the given groups only if they have no other group roles"""
    alumni_role = get_discord_obj(config.guild().roles, "ALUMNI_ROLE")
    group_roles = {group.role for group in await Group.get_groups()}
    for group in groups:
        for member in group.role.members:
            if len(group_roles.intersection(member.roles)) == 1:
                await member.add_roles(alumni_role)
