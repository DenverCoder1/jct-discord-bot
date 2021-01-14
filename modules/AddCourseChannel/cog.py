import discord
import csv
from discord.ext import commands
from modules import new_user
from modules.AddCourseChannel import add_course
from modules.utils.utils import get_discord_obj


class   AddCourseChannel(commands.cog):
    
    def __init__(self,  bot):
        self.bot    =   bot

    @commands.command(name="add_course")

    async def add_course(self,  ctx:    commands.Context,   *args):
     #checking if user is an admin, ie has an admin ID
        if get_discord_object("ADMIN_ROLE-ID") not in  ctx.author.roles:
            ctx.send("Sorry you are not an admin, you are not allowed to add a course. Please contact an admin\
                    if you require further assistance")
        else: 
            ctx.send("Please enter the name of the course you would like to create a channel for")
            course_name =   "-".join(args) #does this correctly input name?
            self.create_channel(ctx,course_name)
        
     '''   if not commands.bot or discord.member.guild.role != 'admin':
            print("Sorry you are not an admin, you are not allowed to add a course. Please contact an admin\
                  if you require further assistance")
        else:
            print("Please enter the name of the course you would like to create a channel for")
            course = ctx.args
            self.create_channel(ctx,course) '''
