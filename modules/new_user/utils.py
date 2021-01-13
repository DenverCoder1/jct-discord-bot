import discord
import discord.utils
from utils.utils import get_discord_obj
import config


async def assign(member: discord.Member, name: str, campus: str, year: int):
	if is_unassigned(member):
		await member.edit(nick=name)
		await add_role(member, campus, year)
		await switch_unassigned(member)


def is_unassigned(member: discord.Member):
	# if the member has the unassigned role
	return get_discord_obj(member.roles, "UNASSIGNED_ROLE_ID") is not None


async def add_role(member: discord.Member, campus: str, year: int):
	"""adds the right role to the user that used the command"""
	# formatting role for csv file, eg LEV_YEAR_1_ROLE_ID
	role_label = f"{campus.upper()}_YEAR_{year}_ROLE_ID"
	class_role = get_discord_obj(member.guild.roles, role_label)

	# check if the role was found
	if class_role == None:
		raise ValueError(f"Could not find the role for {role_label}.")

	await member.add_roles(class_role)
	print(f"Gave {class_role.name} to {member.display_name}")


async def switch_unassigned(member):
	"""removes the unassigned role from member and gives assigned role"""
	# add assigned role
	role = get_discord_obj(member.guild.roles, "ASSIGNED_ROLE_ID")
	await member.add_roles(role)

	# remove unassigned role
	role = get_discord_obj(member.guild.roles, "UNASSIGNED_ROLE_ID")
	await member.remove_roles(role)

	print(f"Removed Unassigned from {member} and added Assigned")


async def give_initial_role(member: discord.Member):
	label = "BOT_ROLE_ID" if member.bot else "UNASSIGNED_ROLE_ID"
	role = get_discord_obj(member.guild.roles, label)
	await member.add_roles(get_discord_obj(member.guild.roles, label))
	print(f"Gave {role.name} to {member.name}")


async def server_greet(member: discord.Member):
	# Sets the channel to the welcome channel and sends a message to it
	channel = get_discord_obj(member.guild.channels, "WELCOME_CHANNEL_ID")
	await channel.send(f"{member.name} joined the server!")
	await channel.send(
		f"""Welcome to the server, {member.mention}!

Please type the following command so we know who you are:

{config.prefix}join **first-name**, **last-name**, **campus**, **year**

Where:
  - **first-name** is your first name,
  - **last-name** is your last name,
  - **campus** is *Lev* or *Tal* (case insensitive),
  - **year** is one of 1, 2, 3, or 4

If you have any trouble feel free to contact an admin using @Admin.
"""
	)


async def private_greet(member: discord.Member):
	"""privately messages the user who joined"""
	if member.dm_channel == None:
		await member.create_dm()

	channel = get_discord_obj(member.guild.channels, "WELCOME_CHANNEL_ID")

	await member.dm_channel.send(
		f"""Welcome to the server, {member.mention}!

If you haven't already done so, please type head over to the {channel.mention} channel in the JCT CompSci ESP server and type the following command so we know who you are:

{config.prefix}join **first-name**, **last-name**, **campus**, **year**

Where:
  - **first-name** is your first name,
  - **last-name** is your last name,
  - **campus** is *Lev* or *Tal* (case insensitive),
  - **year** is one of 1, 2, 3, or 4

If you have any trouble feel free to contact an admin using @Admin in the {channel.mention} channel.
"""
	)