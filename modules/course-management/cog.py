import discord

# from discord import Forbidden
import csv
from discord.ext.commands import has_permissions
import config
from discord.ext import commands
from modules import new_user
from modules.AddCourseChannel import add_course
# from modules.new_user import utils


class AddCourseChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permissions(manage_channels=True)
    # except discord.Forbidden:
    #     await ctx.send('I do not have permission to delete this role')
    @commands.command(name="addcourse")
    # async def add_course(self, ctx, channel_name: str, full_course_name: str = None, *args):#ctx: commands.Context, *args,):
    #     names = " ".join(args)
    #     print("this is args ", args)
    #     split_names = names.split(",")
    #     print("this is split name ", split_names)
    #     channel_name = split_names[0]
    #     if full_course_name:
    #         full_course_name = split_names[1]
    #     else:
    #         full_course_name = channel_name.strip().replace("-", " ")
    #         full_course_name.capitalize()
    #
    #     await add_course.create_channel(ctx, channel_name)

    async def add_course(self, ctx, *args):
        names = " ".join(args)
        split_names = names.split(",")
        channel_name = split_names[0]
        #check if the user entered more than one name for the course
        if len(split_names) > 1:
            full_course_name = split_names[1]

        #otherwise just make the course name the channel name with capitalization and no dashes
        else:
            full_course_name = channel_name.strip().replace("-", " ")
            full_course_name.capitalize()
        await add_course.create_channel(ctx, channel_name)

def setup(bot):
    bot.add_cog(AddCourseChannelCog(bot))
