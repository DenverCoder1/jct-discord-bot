import discord
from discord.ext import commands
from dotenv import load_dotenv
import csv
import os
import config
import discord.utils


# @commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        cts.send(
            "Creating  a   new channel:    {channel_name}"
        )  # should {} be in quotes?
        await guild.create_text_channel(channel_name)


# async def give_initial_role(member: discord.Member):
#     label = "BOT_ROLE_ID" if member.bot else "UNASSIGNED_ROLE_ID"
#     role = get_discord_obj(member.guild.roles, label)
#     await member.add_roles(get_discord_obj(member.guild.roles, label))
#     print(f"Gave {role.name} to {member.name}")
#
#
# def get_discord_obj(iterable, label: str):
#     def get_id(label: str):
#         """gets the id of an object that has the given label in the CSV file"""
#         with open(os.path.join("modules", "new_user", "ids.csv")) as csv_file:
#             csv_reader = csv.reader(csv_file, delimiter=",")
#
#             for row in csv_reader:
#                 if row[0] == label:
#                     return int(row[1])
#
#             return None
#
#     return discord.utils.get(iterable, id=get_id(label))
