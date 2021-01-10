import os
from discord.utils import get
import csv

def is_unassigned(member):
	#if the member has the unassigned role
	return (get(member.roles, id=get_id('UNASSIGNED_ROLE_ID')) != None)


async def add_role(ctx, machon, year):
	'''adds the right role to the user that used the command'''
	member = ctx.author

	#formatting role for env file
	role_id = machon.strip(',').upper() + '_YEAR_' + year + "_ROLE_ID" #format example: LEV_YEAR_1_ROLE_ID
	new_role = get(member.guild.roles, id=get_id(role_id))

	#check if the role was legal
	if new_role == None:
		await ctx.send("The Machon or year was wrong. Please try again or contact an admin for help.")
		return
    
	await member.add_roles(new_role)
	print(f"Gave {new_role} to {member}")
    

async def switch_to_assigned(member):
	'''removes the unassigned role from member'''
	#remove unassigned role
	role = get(member.guild.roles, id=get_id("UNASSIGNED_ROLE_ID"))
	await member.remove_roles(role)

	#add assigned role
	role = get(member.guild.roles, id=get_id("ASSIGNED_ROLE_ID"))
	await member.add_roles(role)

	print(f"Removed Unassigned from {member}")
    
    
async def change_nick(member, first_name, last_name):
		'''changes the nick name of the member to their full name'''
		name = first_name.strip(',').capitalize() + ' ' + last_name.strip(',').capitalize()
		await member.edit(nick = name)
		print(f"Set {member} nick to {name}")

def get_id(name):
	'''gets the id of an object that has the name name'''
	with open("modules\\new_user\\IDs.csv") as file:
		for line in file:
			line = line.strip('\n')
			(key, val) = line.split(',')
			if key == name:
				return int(val)

