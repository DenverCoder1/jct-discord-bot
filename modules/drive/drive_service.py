from google.oauth2 import service_account
from googleapiclient.discovery import build

import config


class DriveService:
    def __init__(self, folder_id: str):
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        self.creds = service_account.Credentials.from_service_account_info(
            config.google_config, scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=self.creds)
        self.folder_id = folder_id

    def add_manager(self, email: str) -> bool:
        """Gives write access to the Google Drive folder given an email address"""
        rule = {
            "role": "writer",
            "type": "user",
            "emailAddress": email,
        }
        created_permission = (
            self.service.permissions()
            .create(fileId=self.folder_id, body=rule, fields="id")
            .execute()
        )
        return "id" in created_permission
