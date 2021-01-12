import discord
import csv
from discord.ext import commands
from modules import new_user
from modules.AddCourseChannel import add_course


class AddCourseChannel(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add-course")
    async def addCourse(self, ctx: commands.Context, *args):
        if not commands.bot or discord.member.guild.role != 'admin':
            print("Sorry you are not an admin, you are not allowed to add a course. Please contact an admin\
                  if you require further assistance")
        else:
            print("Please enter the name of the course you would like to create a channel for")
            course = ctx.args
            self.create_channel(ctx,course)
