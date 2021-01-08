import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

if __name__ == "__main__":

    load_dotenv()

	# Discord setup
    TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_GUILD = int(os.getenv('DISCORD_GUILD'))

    #allows privledged intents for monitoring members joining (has to be enabled for the bot in Discord dev)
    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot('~', intents = intents)  # bot command prefix

    # Get the base file names of all the files in the modules folder
    _, _, modules = next(os.walk('./modules'))
    modules = [os.path.splitext(os.path.basename(module))[0] for module in modules]

    for module in modules:
        client.load_extension('modules.' + module)


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

	# Run Discord bot
    client.run(TOKEN)
