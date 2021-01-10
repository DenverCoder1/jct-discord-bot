import discord
from discord.utils import get
import os
from collections.abc import Iterable
import csv
from typing import Dict


async def assign(ctx, attempts: Dict[discord.Member, int]):
	member = ctx.author
	if is_unassigned(member):
		try:
			(first_name, last_name, machon, year) = await parse_join(ctx)

		except TypeError:
			check_attempts(ctx, attempts)
			return

		await change_nick(member, first_name, last_name)
		await add_role(ctx, machon, year)
		await switch_unassigned(member)


def is_unassigned(member: discord.Member):
	# if the member has the unassigned role
	return get(member.roles, id=get_id("UNASSIGNED_ROLE_ID")) != None


def flatten(l):
	for el in l:
		if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
			yield from flatten(el)
		else:
			yield el


async def parse_join(ctx):
	"""formats the command to get all the required arguments"""
	message = ctx.message.content[5:].strip()  # remove ~join

	# parse with commas
	args = [chunk.strip() for chunk in message.split(",")]  # split on commas

	if len(args) < 4:  # if too few arguments
		args = flatten([arg.split(" ") for arg in args])  # try splitting on spaces

	if len(args) < 4:  # if still too few arguments
		await ctx.send(
			"Please check the syntax of the command:\n\n~join **first-name**,"
			" **last-name**, **campus**, **year**\n\n\t\t- **campus**: Lev or Tal (case"
			" insensitive),\n\t\t- **year**: one of 1, 2, 3, or 4"
		)
		return None

	return args


async def add_role(ctx, machon, year):
	"""adds the right role to the user that used the command"""
	member = ctx.author

	# formatting role for env file
	role_id = (
		machon.upper() + "_YEAR_" + year + "_ROLE_ID"
	)  # format example: LEV_YEAR_1_ROLE_ID
	new_role = get(member.guild.roles, id=get_id(role_id))

	# check if the role was legal
	if new_role == None:
		await ctx.send(
			"The Machon or year was wrong. Please try again or contact an admin for"
			" help."
		)
		return

	await member.add_roles(new_role)
	print(f"Gave {new_role} to {member}")


async def switch_unassigned(member):
	"""removes the unassigned role from member and gives assigned role"""
	# remove unassigned role
	role = get(member.guild.roles, id=get_id("UNASSIGNED_ROLE_ID"))
	await member.remove_roles(role)

	# add assigned role
	role = get(member.guild.roles, id=get_id("ASSIGNED_ROLE_ID"))
	await member.add_roles(role)

	print(f"Removed Unassigned from {member} and added Assigned")


async def change_nick(member, first_name, last_name):
	"""changes the nick name of the member to their full name"""
	name = first_name.capitalize() + " " + last_name.capitalize()
	await member.edit(nick=name)
	print(f"Set {member} nick to {name}")


def get_id(name):
	"""gets the id of an object that has the name: name"""
	with open(os.path.join("modules", "new_user", "IDs.csv")) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")

		for row in csv_reader:
			if row[0] == name:
				return int(row[1])

		return None


async def check_attempts(ctx, attempts):
	"""checks and updates the amount of failed attempts that have been made by the user"""
	member = ctx.author.name

	# check is this user needs extra help
	if member not in attempts:
		attempts[member] = 0

	elif attempts[member] >= 2:
		admin = get(ctx.guild.roles, id=get_id("ADMIN_ROLE_ID"))
		await ctx.send(
			f"{admin.mention} I need some help! This user doesn't know how to read!"
		)

	else:
		attempts[member] += 1