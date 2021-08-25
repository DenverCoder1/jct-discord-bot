from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext, InteractionContext
from discord_slash.model import ComponentType
from discord_slash.utils.manage_components import create_select, create_actionrow
from discord_slash.error import IncorrectFormat as EmptyFolderError
import config
from ..drive_commands.discord_components import create_file_options
from ..drive_commands.drive_class import DiscordDrive


class DriveCog(commands.Cog):
	""" Allows for access to the JCT Google Drive """
	# setup functions for bot
	def __init__(self, bot):
		self.bot = bot
		self.drive = DiscordDrive()
		self.link = "https://drive.google.com/drive/folders/1kzlC2ztK8Hf8hi_9szQ7EkfVSf0roxHb"
		self.drive.authenticate(input("Code: "))

	# @cog_ext.cog_subcommand(
	# 	base="drive",
	# 	name="auth",
	# 	description="Access the JCT Google Drive.",
	# 	guild_ids=[config.guild_id],
	# 	options=[
	# 		create_option(
	# 			name="code",
	# 			description="The authentication code for the drive.",
	# 			option_type=SlashCommandOptionType.STRING,
	# 			required=False,
	# 		),
	# 	],
	# )
	# async def auth_link(
	# 	self, 
	# 	ctx : SlashContext,
	# 	code : Optional[str] = None
	# 	):
	# 	if code == None:
	# 		await ctx.send(self.drive.get_auth_url())
	# 	else:
	# 		self.drive.authenticate(code)
	# 		await ctx.send("Authentication successful.")

	@cog_ext.cog_subcommand(
		base="drive",
		name="link",
		description="Access the JCT Google Drive.",
		guild_ids=[config.guild_id],
		options=[],
	)
	async def drive_link(self, ctx : SlashContext):
		await ctx.send(self.link)
	
	@cog_ext.cog_subcommand(
		base="drive",
		name="download",
		description="Download a file from the JCT Google Drive.",
		guild_ids=[config.guild_id],
		options=[],
	)
	async def download_command(self, ctx : SlashContext):
		await ctx.defer()

		select = create_select(
			options=create_file_options(self.drive.get_files(), self.drive.base_directory['id']),
			placeholder="Choose a file",
			min_values=1,
			max_values=1,
			custom_id="download_select"
		)

		await ctx.send(f"In folder: {self.drive.base_directory['title']}", components=[create_actionrow(select)])
	
	@cog_ext.cog_component(
		components="download_select",
		component_type=ComponentType.select,
		)
	async def update_download_menu(self, ctx : InteractionContext):
		# The selected file id is passed as a list, switch it to a variable
		file_id = ctx.selected_options[0]

		# find the name and icon of the file
		for file in ctx.component['options']:
			if file_id == file['value']:
				file_name = file['label']
				icon = file['emoji']['name']
		
		# if option is a file, change it to a download link for the file
		if icon == '⬇':
			await ctx.edit_origin(
				content=f"Download link for {file_name}: {DiscordDrive.get_download_link(file_id)}",
				components=None,
			)

		# if option is a google app, change it to a link for the app
		elif icon == '🔗':
			await ctx.edit_origin(
				content=f"Link to Google file for {file_name}: {DiscordDrive.get_drive_link(file_id)}",
				components=None,
				)
		
		# if option is a folder or go back, update the select menu
		else:
			try:
				# Edit the message to have a new menu for the selected folder
				select = create_select(
					options=self.drive.get_folder_options(ctx.origin_message_id, file_id),
					placeholder="Choose a file",
					min_values=1,
					max_values=1,
					custom_id="download_select"
				)
				await ctx.edit_origin(
					content=f"In folder {file_name}:",
					components=[create_actionrow(select)]
					)
			
			# if there is nothing in the folder, start back from the base directory
			except EmptyFolderError:
				select = create_select(
					options=self.drive.get_folder_options(self.drive.base_directory['id']),
					placeholder="Choose a file",
					min_values=1,
					max_values=1,
					custom_id="download_select",
					)

				await ctx.edit_origin(
					content=f"Folder is empty, please try again.\nIn folder {self.drive.base_directory['title']}:",
					components=[create_actionrow(select)],
					)


def setup(bot):
	bot.add_cog(DriveCog(bot))