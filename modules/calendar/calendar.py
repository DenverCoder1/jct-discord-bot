from typing import Iterable, Dict
import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import dateparser


class Calendar:
	def __init__(self):
		SCOPES = ["https://www.googleapis.com/auth/calendar"]
		self.creds = service_account.Credentials.from_service_account_info(
			config.google_config, scopes=SCOPES
		)
		self.service = build("calendar", "v3", credentials=self.creds)
		# TODO: get calendar IDs from database
		self.calendar_id = "06m1vlh9ontrnlu1okgsi4vtmo@group.calendar.google.com"
		self.default_time_zone = "Asia/Jerusalem"
		self.dateparser_settings = {
			"TIMEZONE": self.default_time_zone,
			"PREFER_DATES_FROM": "future",
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
			),
		}

	def fetch_upcoming(self) -> Iterable[dict]:
		"""Fetch upcoming events from the calendar"""
		# get the current date and time ('Z' indicates UTC time)
		now = datetime.datetime.utcnow().isoformat() + "Z"
		# fetch results from the calendar API
		events_result = (
			self.service.events()
			.list(
				calendarId=self.calendar_id,
				timeMin=now,
				maxResults=5,
				singleEvents=True,
				orderBy="startTime",
			)
			.execute()
		)
		# return list of events
		return events_result.get("items", [])

	def add_event(
		self,
		summary: str,
		start: str,
		end: str,
		location: str = "",
		description: str = "",
	) -> Dict[str, str]:
		# parse start date
		start_date = dateparser.parse(start, settings=self.dateparser_settings)
		# parse end date
		end_date = dateparser.parse(
			end, settings={**self.dateparser_settings, "RELATIVE_BASE": start_date}
		)
		# check if dates did not parse as None
		if not start_date or not end_date:
			raise ValueError("Dates could not be parsed.")
		# if the end date is before the start date, update the date to starting date
		if end_date < start_date:
			raise ValueError("End date must be before start date.")

		# create request body
		event_details = {
			"summary": summary,
			"location": location,
			"description": description,
			"start": {
				"dateTime": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
				"timeZone": self.default_time_zone,
			},
			"end": {
				"dateTime": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
				"timeZone": self.default_time_zone,
			},
		}

		# Add event to the calendar
		event = (
			self.service.events()
			.insert(calendarId=self.calendar_id, body=event_details)
			.execute()
		)

		return event

	def delete_event(self, event_id: str) -> None:
		# delete event
		self.service.events().delete(
			calendarId=self.calendar_id, eventId=event_id
		).execute()

	def add_manager(self, email: str) -> Dict[str, str]:
		rule = {"scope": {"type": "user", "value": email,}, "role": "writer"}
		created_rule = (
			self.service.acl().insert(calendarId=self.calendar_id, body=rule).execute()
		)
		return created_rule
