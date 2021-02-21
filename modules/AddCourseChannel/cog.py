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
    async def add_course(self, ctx: commands.Context, *args):

        names = " ".join(args)
        split_names = names.split(",")

        course_name = split_names[0]
        update_course_name = course_name.strip().replace(" ", "-")
        update_course_name.lower()

        await add_course.create_channel(
                ctx, update_course_name)


def setup(bot):
    bot.add_cog(AddCourseChannelCog(bot))
