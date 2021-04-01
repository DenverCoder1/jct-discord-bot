import discord
import discord.utils
from modules.error.friendly_error import FriendlyError
from utils.utils import get_discord_obj, embed_success

async def create_channel(ctx, channel_name):
    guild = ctx.guild
    category = get_discord_obj(guild.categories, "COURSES_CATEGORY")

    if discord.utils.get(category.text_channels, name=channel_name) is not None:
        raise FriendlyError("this channel already exists. Please try again.", ctx.channel, ctx.author)
    position = category.text_channels[-1].position+1

    for channel in category.text_channels:
        if channel.name > channel_name:
            position = channel.position-1
            break

    await category.create_text_channel(channel_name, position=position)

    await ctx.send(embed=embed_success("Nice! You created a new channel."))
