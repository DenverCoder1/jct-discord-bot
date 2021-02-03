import os
from dotenv.main import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

class Calendar:
	def __init__(self):
		load_dotenv()
		SCOPES = ['https://www.googleapis.com/auth/calendar']
		CLIENT_CONFIG = {
			"type": "service_account",
			"project_id": os.getenv("GOOGLE_PROJECT_ID"),
			"private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
			"private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
			"client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
			"client_id": os.getenv("GOOGLE_CLIENT_ID"),
			"auth_uri": "https://accounts.google.com/o/oauth2/auth",
			"token_uri": "https://oauth2.googleapis.com/token",
			"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
			"client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
		}
		self.creds = service_account.Credentials.from_service_account_info(
			CLIENT_CONFIG,
			scopes=SCOPES
		)
		self.service = build('calendar', 'v3', credentials=self.creds)
		self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")

	def get_links(self) -> dict:
		return {
			"Add to Google Calendar": (
				"https://calendar.google.com/calendar/render"
				f"?cid=https://www.google.com/calendar/feeds/{self.calendar_id}/public/basic"
			),
			"View the Events": (
				"https://calendar.google.com/calendar/u/0/embed"
				f"?src={self.calendar_id}&ctz=Asia/Jerusalem"
			),
			"iCal Format": (
				"https://calendar.google.com/calendar/ical/"
				f"{self.calendar_id.replace('@','%40')}/public/basic.ics"
			)
		}

	def fetch_upcoming(self) -> str:
		"""Fetch upcoming events from the calendar"""
		# get the current date and time ('Z' indicates UTC time)
		now = datetime.datetime.utcnow().isoformat() + 'Z'
		# fetch results from the calendar API
		events_result = self.service.events().list(
			calendarId=self.calendar_id,
			timeMin=now,
			maxResults=5,
			singleEvents=True,
			orderBy='startTime'
		).execute()
		# return list of events
		return events_result.get('items', [])