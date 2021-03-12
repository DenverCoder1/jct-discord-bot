from .calendar import Calendar
from .event import Event
from utils.utils import parse_date
from typing import Iterable, Dict
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
import config


class CalendarService:
	def __init__(self):
		SCOPES = ["https://www.googleapis.com/auth/calendar"]
		self.creds = service_account.Credentials.from_service_account_info(
			config.google_config, scopes=SCOPES
		)
		self.service = build("calendar", "v3", credentials=self.creds)
		self.timezone = "Asia/Jerusalem"

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
		self,
		calendar_id: str,
		max_results: int,
		query: str = "",
		page_token: str = None,
	) -> Iterable[Event]:
		"""Fetch upcoming events from the calendar"""
		# get the current date and time ('Z' indicates UTC time)
		now = datetime.utcnow().isoformat() + "Z"
		# fetch results from the calendar API
		events_result = (
			self.service.events()
			.list(
				calendarId=calendar_id,
				timeMin=now,
				maxResults=max_results,
				singleEvents=True,
				orderBy="startTime",
				pageToken=page_token,
			)
			.execute()
		)
		# get next page token
		next_page_token = events_result.get("nextPageToken")
		# return list of events
		events = events_result.get("items", [])
		# filter by search term
		query = query.lower()
		filtered = filter(lambda item: query in item.get("summary").lower(), events)
		# convert dicts to Event objects
		converted_events = tuple(map(lambda item: Event(item, self.timezone), filtered))
		# return events and the next page's token
		return converted_events, next_page_token

	def add_event(
		self,
		calendar_id: str,
		summary: str,
		start: str,
		end: str,
		location: str = "",
		description: str = "",
	) -> Event:
		"""Add an event to the calendar given the id, summary, start time,
		and optionally, the end time, location and description."""
		all_day = False
		# parse start date
		start_date = parse_date(
			start, from_tz=self.timezone, to_tz=self.timezone, future=True
		)
		# check start date
		if start_date is None:
			raise ValueError(f'Start date "{start}" could not be parsed.')
		# parse end date
		if end is not None:
			end_date = parse_date(
				end,
				from_tz=self.timezone,
				to_tz=self.timezone,
				future=True,
				base=start_date,
			)
		else:
			# if no end date was specified, use the start time
			end_date = start_date
			# if words suggest no time was specified, make it an all day event
			time_words = (" at ", " from ", "am ", " midnight ", ":")
			if start_date.time() == datetime.min.time() and not any(
				word in f" {start} " for word in time_words
			):
				all_day = True
		# check end date
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
			"start": (
				{
					"dateTime": start_date.isoformat("T", "seconds"),
					"timeZone": self.timezone,
				}
				if not all_day
				else {"date": start_date.date().isoformat()}
			),
			"end": (
				{
					"dateTime": end_date.isoformat("T", "seconds"),
					"timeZone": self.timezone,
				}
				if not all_day
				else {"date": end_date.date().isoformat()}
			),
		}
		# Add event to the calendar
		event = (
			self.service.events()
			.insert(calendarId=calendar_id, body=event_details)
			.execute()
		)
		return Event(event, self.timezone)

	def delete_event(self, calendar_id: str, event: Event) -> None:
		"""Delete an event from a calendar given the calendar id and event object"""
		# delete event
		response = (
			self.service.events()
			.delete(calendarId=calendar_id, eventId=event.id())
			.execute()
		)
		# response should be empty if successful
		if response != "":
			raise ConnectionError("Couldn't delete event.", response)

	def update_event(self, calendar_id: str, event: Event, **kwargs) -> Event:
		"""Update an event from a calendar given the calendar id, event object, and parameters to update"""
		# parse new event title if provided
		new_summary = (
			kwargs.get("title", None)
			or kwargs.get("summary", None)
			or kwargs.get("name", None)
		)
		# get new location if provided
		new_location = kwargs.get("location", None)
		# get new description if provided
		new_desc = kwargs.get("description", None)
		# parse new start date if provided
		new_start_date = parse_date(
			kwargs.get("start", None),
			from_tz=self.timezone,
			to_tz=self.timezone,
			base=event.start(),
		)
		# parse new end date if provided
		new_end_date = parse_date(
			kwargs.get("end", None),
			from_tz=self.timezone,
			to_tz=self.timezone,
			base=(new_start_date if new_start_date else event.end()),
		)
		# create request body
		event_details = {
			**event.details,
			**({"summary": new_summary} if type(new_summary) == str else {}),
			**({"location": new_location} if type(new_location) == str else {}),
			**({"description": new_desc} if type(new_desc) == str else {}),
			"start": {
				"timeZone": self.timezone,
				"dateTime": (
					new_start_date if new_start_date is not None else event.start()
				).isoformat("T", "seconds"),
			},
			"end": {
				"timeZone": self.timezone,
				"dateTime": (
					new_end_date if new_end_date is not None else event.end()
				).isoformat("T", "seconds"),
			},
		}
		# check that new time range is valid
		new_event = Event(event_details)
		new_start_date = new_event.start().replace(tzinfo=None)
		new_end_date = new_event.end().replace(tzinfo=None)
		if new_end_date < new_start_date:
			raise ValueError("The start time must come before the end time.")
		# update the event
		updated_event = (
			self.service.events()
			.update(calendarId=calendar_id, eventId=event.id(), body=event_details)
			.execute()
		)
		return Event(updated_event)

	def create_calendar(self, summary: str) -> Calendar:
		"""Creates a new public calendar on the service account given the name
		Returns the calendar object"""
		# create the calendar
		calendar = {"summary": summary, "timeZone": self.timezone}
		created_calendar = Calendar(
			self.service.calendars().insert(body=calendar).execute()
		)
		# make calendar public
		rule = {"scope": {"type": "default"}, "role": "reader"}
		self.service.acl().insert(calendarId=created_calendar.id, body=rule).execute()
		# return the calendar object
		return created_calendar

	def get_calendar_list(self) -> Iterable[Calendar]:
		"""Returns a complete list of calendars on the service account"""
		page_token = None
		calendars = []
		while True:
			calendar_list = (
				self.service.calendarList().list(pageToken=page_token).execute()
			)
			calendars += map(lambda item: Calendar(item), calendar_list["items"])
			page_token = calendar_list.get("nextPageToken")
			if not page_token:
				break
		return calendars

	def add_manager(self, calendar_id: str, email: str) -> bool:
		"""Gives write access to a user for a calendar given an email address"""
		rule = {"scope": {"type": "user", "value": email,}, "role": "writer"}
		created_rule = (
			self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
		)
		# returns True if the rule was applied successfully
		return created_rule["id"] == f"user:{email}"