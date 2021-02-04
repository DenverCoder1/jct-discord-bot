from typing import Iterable, Dict
import os
from dotenv.main import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import dateparser

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
		self.default_time_zone = "Asia/Jerusalem"
		self.dateparser_settings = {
			'TIMEZONE': self.default_time_zone,
			'PREFER_DATES_FROM': 'future'
		}

	def get_links(self) -> Dict[str, str]:
		return {
			"Add to Google Calendar": (
				"https://calendar.google.com/calendar/render"
				f"?cid=https://www.google.com/calendar/feeds/{self.calendar_id}"
				"/public/basic"
			),
			"View the Events": (
				"https://calendar.google.com/calendar/u/0/embed"
				f"?src={self.calendar_id}&ctz=Asia/Jerusalem"
			),
			"iCal Format": (
				"https://calendar.google.com/calendar/ical"
				f"/{self.calendar_id.replace('@','%40')}/public/basic.ics"
			)
		}

	def fetch_upcoming(self) -> Iterable[dict]:
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

	def add_event(
		self,
		summary: str,
		start: str, 
		end: str,
		location: str = "", 
		description: str = "", 
	) -> Dict[str, str]:
		start_date = dateparser.parse(start, settings=self.dateparser_settings)
		end_date = dateparser.parse(end, settings=self.dateparser_settings)
		if not start_date or not end_date:
			raise ValueError("Dates could not be parsed.")
		# if the end date is before the start date,
		# update the date to starting date
		if end_date < start_date:
			shifted_end_date = end_date.replace(
				year=start_date.year,
				month=start_date.month, 
				day=start_date.day
			)
			# even if date is shifted, the time doesn't work
			if shifted_end_date < start_date:
				raise ValueError("End date must be before start date.")
			else:
				end_date = shifted_end_date

		# create request body
		event_details = {
			'summary': summary,
			'location': location,
			'description': description,
			'start': {
				'dateTime': start_date.strftime("%Y-%m-%dT%H:%M:%S"),
				'timeZone': self.default_time_zone,
			},
			'end': {
				'dateTime': end_date.strftime("%Y-%m-%dT%H:%M:%S"),
				'timeZone': self.default_time_zone,
			},
		}
		
		# Add event to the calendar
		event = self.service.events().insert(
			calendarId=self.calendar_id,
			body=event_details
		).execute()

		return event

	def add_manager(self, email: str) -> Dict[str, str]:
		rule = {
			'scope': {
				'type': 'user',
				'value': email,
			},
			'role': 'writer'
		}
		created_rule = self.service.acl().insert(
			calendarId=self.calendar_id,
			body=rule
		).execute()
		return created_rule