from functools import cache
import random
from utils import utils
from database import sql_fetcher
import discord
from pyluach.dates import HebrewDate
import config


@cache
def __unassigned_role() -> discord.Role:
	role = config.guild().get_role(utils.get_id("UNASSIGNED_ROLE"))
	assert role is not None
	return role


@cache
def __student_role() -> discord.Role:
	role = config.guild().get_role(utils.get_id("STUDENT_ROLE"))
	assert role is not None
	return role


@cache
def __welcome_channel() -> discord.TextChannel:
	channel = config.guild().get_channel(utils.get_id("OFF_TOPIC_CHANNEL"))
	assert isinstance(channel, discord.TextChannel)
	return channel


async def assign(member: discord.Member, name: str, campus_id: int, year: int):
	if __unassigned_role() in member.roles:
		await member.edit(nick=name)
		await __add_role(member, campus_id, year)
		await member.add_roles(__student_role())
		await member.remove_roles(__unassigned_role())
		print(f"Removed Unassigned from {member} and added Student")
		await server_welcome(member)


async def __add_role(member: discord.Member, campus_id: int, year: int):
	"""adds the right role to the user that used the command"""
	today = HebrewDate.today()
	last_elul_year = today.year if today.month == 6 else today.year - 1
	last_elul = HebrewDate(last_elul_year, 6, 1)
	base_year = last_elul.to_pydate().year
	grad_year = base_year + 4 - year

	query = sql_fetcher.fetch("modules", "join", "queries", "get_role.sql")
	with config.conn as conn:
		with conn.cursor() as cursor:
			cursor.execute(query, {"campus_id": campus_id, "grad_year": grad_year})
			role_id = cursor.fetchone()[0]

	class_role = config.guild().get_role(role_id)
	assert class_role is not None
	await member.add_roles(class_role)
	print(f"Gave {class_role.name} to {member.display_name}")


async def server_welcome(member: discord.Member):
	# Sets the channel to the welcome channel and sends a message to it
	welcome_emojis = ["🎉", "👋", "🌊", "🔥", "😎", "👏", "🎊", "🥳", "🙌", "✨", "⚡"]
	random_emoji = random.choice(welcome_emojis)
	nth = utils.ordinal(len(__student_role().members))
	await __welcome_channel().send(
		f"Everyone welcome our {nth} student {member.mention} to the"
		f" server! Welcome! {random_emoji}"
	)
