import os
from dotenv import load_dotenv
from discord.ext import commands

if __name__ == "__main__":

	load_dotenv()

	# Discord setup
	TOKEN = os.getenv('DISCORD_TOKEN')
	DISCORD_GUILD = int(os.getenv('DISCORD_GUILD'))
	client = commands.Bot('~')  # bot command prefix

	# Get the base file names of all the files in the modules folder
	files = [f for f in os.listdir('modules') if os.path.isfile('modules/' + f)]
	modules = [os.path.splitext(os.path.basename(file))[0] for file in files]

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
