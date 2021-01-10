import os
from discord.utils import get
<<<<<<< Updated upstream

def is_new(member):
    #if the member has the unassigned role
    if get(member.roles, id = int(os.getenv('UNASSIGNED_ROLE_ID'))) != None:
        return True
    return False


async def add_role(ctx, machon, year):
    member = ctx.author
    
    #formatting role for env file
    role_id = machon.upper() + '_YEAR_' + year + "_ROLE_ID" #format example: LEV_YEAR_1_ROLE_ID
    new_role = get(member.guild.roles, id = int(os.getenv(role_id)))

    #check if the role was legal
    if new_role == None:
        await ctx.send("The Machon or year was wrong. Please try again or contact an admin for help.")
        return
    
    await member.add_roles(new_role)
    print(f"Gave {new_role} to {member}")
    

async def remove_unassigned(member):
    role = get(member.guild.roles, id = int(os.getenv("UNASSIGNED_ROLE_ID")))
    await member.remove_roles(role)
    print(f"Removed Unassigned from {member}")
    
    
async def change_nick(member, first_name, last_name):
        name = first_name + ' ' + last_name
        await member.edit(nick = name)
        print(f"Set {member} nick to {name}")


    


        

    
=======
import csv

def is_unassigned(member):
	#if the member has the unassigned role
	return (get(member.roles, id=int(get_id('UNASSIGNED_ROLE_ID'))) != None)


async def add_role(ctx, machon, year):
	'''adds the right role to the user that used the command'''
	member = ctx.author

	#formatting role for env file
	role_id = machon.upper() + '_YEAR_' + year + "_ROLE_ID" #format example: LEV_YEAR_1_ROLE_ID
	new_role = get(member.guild.roles, id = int(get_id(role_id)))

	#check if the role was legal
	if new_role == None:
		await ctx.send("The Machon or year was wrong. Please try again or contact an admin for help.")
		return
    
	await member.add_roles(new_role)
	print(f"Gave {new_role} to {member}")
    

async def remove_unassigned(member):
	'''removes the unassigned role from member'''
	role = get(member.guild.roles, id = int(get_id("UNASSIGNED_ROLE_ID")))
	await member.remove_roles(role)
	print(f"Removed Unassigned from {member}")
    
    
async def change_nick(member, first_name, last_name):
		'''changes the nick name of the member to their full name'''
		name = first_name.capitalize() + ' ' + last_name.capitalize()
		await member.edit(nick = name)
		print(f"Set {member} nick to {name}")

def get_id(name):
	'''gets the id of an object that has the name name'''
	with open(os.getcwd() +"\\modules\\new_user\\IDs.csv") as file:
		for line in file:
			line = line.strip('\n')
			(key, val) = line.split('=')
			if key == name:
				return val


>>>>>>> Stashed changes
