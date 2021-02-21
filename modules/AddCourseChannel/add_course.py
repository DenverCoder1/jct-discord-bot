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
    categoryFlag = False
    channelFlag = False
    print("category name and channel name ", category_name, " ", channel_name)
    # if category_name != "none":  # if user entered a category name
    # existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
    # if not existing_category:  # if category doesn't exist create it
    #     await guild.create_category_channel(category_name)
    # channels = discord.get.CategoryChannel.text_channels
    # if channel_name not in channels:
    #     print("blah blah")

    #if category_name not in ctx.guild.categories:
    for category in ctx.guild.categories:
        print("categoryFlag and category ", categoryFlag, category)
        print("category type is:", type(category))
        if category == category_name:
            categoryFlag = True
            break

    for channel in ctx.guild.text_channels:
        if channel == channel_name:
            channelFlag = True
            break
    if channelFlag == True:
        await ctx.send("Sorry this channel already exists. Please try again.")
        return
    else:
        if categoryFlag == False:
            await guild.create_category_channel(category_name)

    #NEED to try getting the category ID for the category name they passed in and try creating the channel with that instead
    await guild.create_text_channel(channel_name, category=category_name)
    await ctx.send("Nice! You created a new channel.")

    # existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    # if not existing_channel:
    #     if category_name != "none":
    #         await guild.create_text_channel(channel_name, category_name)
    #     else:
    #         await guild.create_text_channel(channel_name)

    #     await ctx.send("Nice! You created a new channel.")
