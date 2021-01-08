# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 12:49:48 2021

@author: pinny
"""

from discord import utils

def is_new(member):
    if utils.get(member.roles, name="Unassigned") != None:
        return True
    return False

async def add_role(ctx, machon, year):
        member = ctx.author
    
        #adjusts the name to be specific to a role and assigns the role object to new_role
        role_name = machon.capitalize() + ' ' + year
        new_role = utils.get(member.guild.roles, name = role_name)

        #check if the role was legal
        if new_role == None:
            await ctx.send("Illegal Machon or Year. Please try again.")
        
        await member.add_roles(new_role)
        print(f"Gave {new_role} to {member}")

async def remove_unassigned(member):
    role = utils.get(member.guild.roles, name = "Unassigned")
    await member.remove_roles(role)
    print(f"Removed Unassigned from {member}")
    
async def change_nick(member, first_name, last_name):
        name = first_name + ' ' + last_name
        await member.edit(nick = name)
        print(f"Set {member} nick to {name}")


    


        

    