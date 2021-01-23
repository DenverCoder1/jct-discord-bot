import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import csv
import os
import config
import discord.utils

# @has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not existing_channel:
        # should {} be in quotes?
        await guild.create_text_channel(channel_name)
        await ctx.send("Nice! You created a new channel.")

