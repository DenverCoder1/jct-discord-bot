import discord
from discord.ext import commands
from discord import logging
import traceback
from modules.error_log.utils import get_discord_obj, get_logs, log_to_file


class ErrorLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="logs")
    async def logs(self, ctx, *args):
        """Show recent logs from err.log"""
        # log in console that a ping was received
        print('Executing command "logs".')
        # reply with last 1200 characters of log file
        await ctx.send(f"```...{get_logs('err.log')[-1200:]}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        """test discord exception by typing 'raise-exception' in a message"""
        if message.content == 'raise-exception':
            raise discord.DiscordException


async def on_error(event, *args, **kwargs):
    """When an exception is raised, log it in err.log and bot log channel"""
    msg = args[0]  # gets the message object
    log_channel = get_discord_obj(msg.guild.channels, "JCT_BOT_LOG_CHANNEL_ID")
    # handle message error
    if hasattr(msg, "content"):
        trace = traceback.format_exc()  # formats the error as traceback
        logging.warning(trace)  # logs error as warning in console
        log_to_file("err.log", trace)  # log to err.log
        await msg.channel.send("You caused an error!")  # notify user of error
        # format error for bot log channel
        error_message = (
            "Message info:\n```"
            f"Author:\n{msg.author} ({msg.author.nick})\n\n"
            f"Channel:\n{msg.channel}\n\n"
            f"Content:\n{msg.content}```\n"
            f"Traceback:\n```{trace}```"
        )
        await log_channel.send(error_message)  # log error in bot log channel


async def on_command_error(ctx, error):
    """When a command exception is raised, log it in err.log and bot log channel"""
    log_channel = get_discord_obj(ctx.guild.channels, "JCT_BOT_LOG_CHANNEL_ID")
    logging.warning(error)  # logs error as warning in console
    log_to_file("err.log", error)  # log to err.log
    await ctx.channel.send(error)  # notify user of error
    # format error for bot log channel
    error_message = (
        "Message info:\n```"
        f"Message author:\n{ctx.author} ({ctx.author.nick})\n\n"
        f"Message channel:\n{ctx.channel}\n\n"
        f"Message content:\n{ctx.message.content}```\n"
        f"Error:\n```{error}```"
    )
    await log_channel.send(error_message)  # log error in bot log channel


# setup functions for bot
def setup(bot):
    bot.add_cog(ErrorLogCog(bot))
    bot.on_error = on_error
    bot.on_command_error = on_command_error
