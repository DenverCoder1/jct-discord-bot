import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import csv
import os
import config
import discord.utils
from discord import CategoryChannel


async def create_channel(ctx, channel_name, category_name):
    guild = ctx.guild
    if category_name != "none":  # if user entered a category name
        # existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
        # if not existing_category:  # if category doesn't exist create it
        #     await guild.create_category_channel(category_name)
        channels = discord.get.CategoryChannel.text_channels
    if channel_name not in channels:
        print("blah blah")

    # existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    # if not existing_channel:
    if category_name != "none":
        await guild.create_text_channel(channel_name, category_name)
    else:
        await guild.create_text_channel(channel_name)

    await ctx.send("Nice! You created a new channel.")
