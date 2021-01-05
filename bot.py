import os
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands

load_dotenv()

# Discord setup
TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = int(os.getenv('DISCORD_GUILD'))
client = Bot('~')  # bot command prefix


@client.event
async def on_ready():
    '''When discord is connected'''
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_error(event, *args, **kwargs):
    '''When an exception is raised, log it in err.log'''
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            f.write(f'Event: {event}\nMessage: {args}\n')


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def ping(ctx):
    '''Command to receive a response from the bot.
       Invoked with !ping'''
    # log command in console
    print("Received ping!")
    # respond to command
    await ctx.send("Received ping!")

# Run Discord bot
client.run(TOKEN)
