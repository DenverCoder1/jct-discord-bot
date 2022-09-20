from functools import cache
import random
from utils import utils
from database import sql
import nextcord
from pyluach.dates import HebrewDate
import config


@cache
def __unassigned_role() -> nextcord.Role:
	role = config.guild().get_role(utils.get_id("UNASSIGNED_ROLE"))
	assert role is not None
	return role


@cache
def __student_role() -> nextcord.Role:
	role = config.guild().get_role(utils.get_id("STUDENT_ROLE"))
	assert role is not None
	return role


@cache
def __welcome_channel() -> nextcord.TextChannel:
	channel = config.guild().get_channel(utils.get_id("OFF_TOPIC_CHANNEL"))
	assert isinstance(channel, nextcord.TextChannel)
	return channel


async def assign(member: nextcord.Member, name: str, campus_id: int, year: int):
	"""Assigns a user who joined the server.

	Sets the user's nickname to their full name, adds the role for the class they're in, and replaces the unassigned role with the assigned role. Following this, it welcomes the user in #off-topic.

	Args:
		member (nextcord.Member): The member to assign.
		name (str): The member's full name.
		campus_id (int): The ID of the campus they study in.
		year (int): The index of the year they're in. This should be a number from 1 to 4.
	"""
	if __unassigned_role() in member.roles:
		await member.edit(nick=name)
		await __add_role(member, campus_id, year)
		await member.add_roles(__student_role())
		await member.remove_roles(__unassigned_role())
		await server_welcome(member)


async def __add_role(member: nextcord.Member, campus_id: int, year: int):
	"""adds the right role to the user that used the command"""
	today = HebrewDate.today()
	last_elul_year = today.year if today.month == 6 else today.year - 1
	last_elul = HebrewDate(last_elul_year, 6, 1)
	base_year = last_elul.to_pydate().year
	grad_year = base_year + 4 - year
	role_id = await sql.select.value("groups", "role", campus=campus_id, grad_year=grad_year)
	class_role = config.guild().get_role(role_id)
	assert class_role is not None
	await member.add_roles(class_role)


async def server_welcome(member: nextcord.Member):
	# Sets the channel to the welcome channel and sends a message to it
	welcome_emojis = ["🎉", "👋", "🌊", "🔥", "😎", "👏", "🎊", "🥳", "🙌", "✨", "⚡"]
	random_emoji = random.choice(welcome_emojis)
	nth = utils.ordinal(len(__student_role().members))
	await __welcome_channel().send(
		f"Everyone welcome our {nth} student {member.mention} to the"
		f" server! Welcome! {random_emoji}"
	)
