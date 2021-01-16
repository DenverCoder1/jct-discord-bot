import discord
import csv
from discord.ext import commands
from modules import new_user
from modules.AddCourseChannel import add_course

from modules.new_user.utils import get_discord_obj
from modules.new_user import utils


class AddCourseChannelCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addcourse")
    async def add_course(self, ctx: commands.Context, *args):
        # checking if user is an admin, ie has an admin ID
        if self.get_discord_object("ADMIN_ROLE-ID") not in ctx.author.roles:
            await ctx.send(
                "Sorry you are not an admin, you are not allowed to add a course. Please contact an admin if you "
                "require further assistance")
        else:
            await ctx.send("Please enter the name of the course you would like to create a channel for")
            course_name = "-".join(args)  # does this correctly input name?
            course_name.lower()
            self.create_channel(ctx, course_name)

    '''   if not commands.bot or discord.member.guild.role != 'admin':
           print("Sorry you are not an admin, you are not allowed to add a course. Please contact an admin\
                 if you require further assistance")
       else:
           print("Please enter the name of the course you would like to create a channel for")
           course = ctx.args
           self.create_channel(ctx,course) '''


def setup(bot):
    bot.add_cog(AddCourseChannelCog(bot))
