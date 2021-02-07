from typing import Iterable, Dict
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import dateparser
import config


class Calendar:
	def __init__(self):
		SCOPES = ["https://www.googleapis.com/auth/calendar"]
		self.creds = service_account.Credentials.from_service_account_info(
			config.google_config, scopes=SCOPES
		)
		self.service = build("calendar", "v3", credentials=self.creds)
		self.default_time_zone = "Asia/Jerusalem"
		self.dateparser_settings = {
			"TIMEZONE": self.default_time_zone,
			"PREFER_DATES_FROM": "future",
		}

	def get_links(self, calendar_id: str) -> Dict[str, str]:
		"""Get a dict of links for adding and viewing a given Google Calendar"""
		return {
			"Add to Google Calendar": (
				"https://calendar.google.com/calendar/render"
				f"?cid=https://www.google.com/calendar/feeds/{calendar_id}"
				"/public/basic"
			),
			"View the Events": (
				"https://calendar.google.com/calendar/u/0/embed"
				f"?src={calendar_id}&ctz=Asia/Jerusalem"
			),
			"iCal Format": (
				"https://calendar.google.com/calendar/ical"
				f"/{calendar_id.replace('@','%40')}/public/basic.ics"
			),
		}

	def fetch_upcoming(
		self, calendar_id: str, max_results: int, query: str = ""
	) -> Iterable[dict]:
		"""Fetch upcoming events from the calendar"""
		# get the current date and time ('Z' indicates UTC time)
		now = datetime.datetime.utcnow().isoformat() + "Z"
		# fetch results from the calendar API
		events_result = (
			self.service.events()
			.list(
				calendarId=calendar_id,
				timeMin=now,
				maxResults=max_results,
				singleEvents=True,
				orderBy="startTime",
			)
			.execute()
		)
		# return list of events
		items = events_result.get("items", [])
		# filter by search term
		query = query.lower()
		events = filter(lambda item: query in item.get("summary").lower(), items)
		return list(events)

	def add_event(
		self,
		calendar_id: str,
		summary: str,
		start: str,
		end: str,
		location: str = "",
		description: str = "",
	) -> Dict[str, str]:
		"""Add an event to the calendar given the id, summary, start time,
		and optionally, the end time, location and description."""
		# parse start date
		start_date = dateparser.parse(start, settings=self.dateparser_settings)
		# parse end date
		if end is not None and start_date is not None:
			end_date = dateparser.parse(
				end, settings={**self.dateparser_settings, "RELATIVE_BASE": start_date}
			)
		elif start_date is None:
			raise ValueError(f'Start date "{start}" could not be parsed.')
		else:
			end_date = start_date
		# check if dates did not parse as None
		if end_date is None:
			raise ValueError(f'End date "{end}" could not be parsed.')
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
			.insert(calendarId=calendar_id, body=event_details)
			.execute()
		)

		return event

	def delete_event(self, calendar_id: str, event_id: str) -> None:
		"""Delete an event from a calendar given the calendar id and event id"""
		# delete event
		self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

	def create_calendar(self, summary: str) -> Dict[str, str]:
		"""Creates a new public calendar on the service account given the name"""
		# create the calendar
		calendar = {"summary": summary, "timeZone": self.default_time_zone}
		created_calendar = self.service.calendars().insert(body=calendar).execute()
		# make calendar public
		rule = {"scope": {"type": "default"}, "role": "reader"}
		self.service.acl().insert(
			calendarId=created_calendar["id"], body=rule
		).execute()
		return created_calendar

	def get_calendar_list(self) -> Iterable[dict]:
		"""Returns a complete list of calendars on the service account"""
		page_token = None
		calendars = []
		while True:
			calendar_list = (
				self.service.calendarList().list(pageToken=page_token).execute()
			)
			calendars += calendar_list["items"]
			page_token = calendar_list.get("nextPageToken")
			if not page_token:
				break
		return calendars

	def add_manager(self, calendar_id: str, email: str) -> Dict[str, str]:
		"""Gives write access to a user for a calendar given an email address"""
		rule = {"scope": {"type": "user", "value": email,}, "role": "writer"}
		created_rule = (
			self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
		)
		return created_rule
