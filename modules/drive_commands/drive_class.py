import pydrive2 as pydrive
import os
from discord_slash.context import InteractionContext
from ..error.friendly_error import FriendlyError

class DiscordDrive:
	base_directory = {'id' : '11NVfDSj_bNJIRjInfibndFsNkeJ3ogQX', 'title' : 'Test Folder'} # base directory of the drive {'id' : '1kzlC2ztK8Hf8hi_9szQ7EkfVSf0roxHb', 'name' : 'Computer Science Resources JCT ESP All Courses'}

	def __init__(self):
		# set up settings
		pydrive.auth.GoogleAuth

		# set up authentication settings
		self.gauth = pydrive.auth.GoogleAuth()
		self.gauth.LoadCredentialsFile(os.path.join(self.extra_files_directory, 'credentials.json'))

		# initialize the drive
		self.drive = pydrive.drive.GoogleDrive(self.gauth)

	def get_auth_url(self):
		return self.gauth.GetAuthUrl()

	def authenticate(self, code : str):
		""" OAuth Verification function """
		self.gauth.Auth(code)

	@classmethod
	def get_download_link(cls, file_id):
		""" Get a direct download link for a file """
		return "https://drive.google.com/uc?export=download&id=" + file_id

	@classmethod
	def get_drive_link(cls, file_id):
		return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

	def get_files(self, directory_id):
		""" Returns list of dicts each having the title, id, and icon representing the type of a file"""

		# get a list of the files in the directory
		current_folder = self.drive.ListFile({'q': f"'{directory_id}' in parents and trashed=false"}).GetList()
		
		# create a new option for every file in the directory
		files = []
		for file in current_folder:
			file_type = file.metadata['mimeType']
			
			if file_type == 'application/vnd.google-apps.folder':
				icon = '📁'
			elif file_type.startswith('application/vnd.google-apps'):
				icon = '🔗'
			else:
				icon = '⬇'

			files.insert(
				0,
				{
					'title' : file['title'],
					'id' : file['id'],
					'icon' : icon,
				},
			)

		return files