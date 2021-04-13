from . import html_parser
from .calendar import Calendar
from .event import Event
from utils.utils import parse_date
from typing import Any, Dict, Optional, Sequence
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
import config
from fuzzywuzzy import fuzz


class CalendarService:
	def __init__(self, timezone: str):
		SCOPES = ["https://www.googleapis.com/auth/calendar"]
		self.creds = service_account.Credentials.from_service_account_info(
			config.google_config, scopes=SCOPES
		)
		self.service = build("calendar", "v3", credentials=self.creds)
		self.timezone = timezone

	def get_links(self, calendar: Calendar) -> Dict[str, str]:
		"""Get a dict of links for adding and viewing a given Google Calendar"""
		return {
			"Add to Google Calendar": calendar.add_url(),
			"View the Events": calendar.view_url(self.timezone),
			"iCal Format": calendar.ical_url(),
		}

	def fetch_upcoming(
		self,
		calendar_id: str,
		query: str = "",
		page_token: Optional[str] = None,
		max_results: int = 100,
	) -> Sequence[Event]:
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
		# return list of events
		events = events_result.get("items", [])
		# filter by search term
		clean_query = query.lower().replace(" ", "")
		# convert dicts to Event objects
		converted_events = tuple(
			self.__dict_to_event(dict_)
			for dict_ in events
			if clean_query in dict_["summary"].lower().replace(" ", "")
			or fuzz.token_set_ratio(query, dict_["summary"]) > 75
		)
		# return events and the next page's token
		return converted_events

	def add_event(
		self,
		calendar_id: str,
		summary: str,
		start: str,
		end: Optional[str],
		description: str,
		location: str,
	) -> Event:
		"""Add an event to the calendar given the id, summary, start time,
		and optionally, the end time, location and description."""
		all_day = False
		# parse start date
		start_date = parse_date(start, future=True)
		# check start date
		if start_date is None:
			raise ValueError(f'Start date "{start}" could not be parsed.')
		# parse end date
		if end is not None:
			end_date = parse_date(end, future=True, base=start_date)
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
			"description": html_parser.md_links_to_html(description),
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
		return self.__dict_to_event(event)

	def delete_event(self, calendar_id: str, event: Event) -> None:
		"""Delete an event from a calendar given the calendar id and event object"""
		# delete event
		response = (
			self.service.events()
			.delete(calendarId=calendar_id, eventId=event.id)
			.execute()
		)
		# response should be empty if successful
		if response != "":
			raise ConnectionError("Couldn't delete event.", response)

	def update_event(
		self,
		calendar_id: str,
		event: Event,
		new_summary: Optional[str] = None,
		new_start: Optional[str] = None,
		new_end: Optional[str] = None,
		new_description: Optional[str] = None,
		new_location: Optional[str] = None,
	) -> Event:
		"""Update an event from a calendar given the calendar id, event object, and parameters to update"""
		# parse new start date if provided
		new_start_date = parse_date(new_start, base=event.start) or event.start
		# if the start time is changed, the end time will move with it if it's not specified
		start_delta = new_start_date - event.start
		# parse new end date if provided
		new_end_date = parse_date(
			new_end,
			base=(new_start_date if new_start_date != event.start else event.end),
		) or (event.end + start_delta)
		# check that new time range is valid
		if new_end_date < new_start_date:
			raise ValueError("The start time must come before the end time.")
		# create request body
		event_details = {
			"summary": new_summary or event.title,
			"location": new_location or event.location or "",
			"description": html_parser.md_links_to_html(
				new_description or event.description or ""
			),
			"start": {
				"timeZone": self.timezone,
				"dateTime": new_start_date.isoformat("T", "seconds"),
			},
			"end": {
				"timeZone": self.timezone,
				"dateTime": new_end_date.isoformat("T", "seconds"),
			},
		}
		# update the event
		updated_event = (
			self.service.events()
			.update(calendarId=calendar_id, eventId=event.id, body=event_details)
			.execute()
		)
		return self.__dict_to_event(updated_event)

	def create_calendar(self, summary: str) -> Calendar:
		"""Creates a new public calendar on the service account given the name
		Returns the calendar object"""
		# create the calendar
		calendar = {"summary": summary, "timeZone": self.timezone}
		created_calendar = Calendar.from_dict(
			self.service.calendars().insert(body=calendar).execute()
		)
		# make calendar public
		rule = {"scope": {"type": "default"}, "role": "reader"}
		self.service.acl().insert(calendarId=created_calendar.id, body=rule).execute()
		# return the calendar object
		return created_calendar

	def add_manager(self, calendar_id: str, email: str) -> bool:
		"""Gives write access to a user for a calendar given an email address"""
		rule = {"scope": {"type": "user", "value": email,}, "role": "writer"}
		created_rule = (
			self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
		)
		# returns True if the rule was applied successfully
		return created_rule["id"] == f"user:{email}"

	def __dict_to_event(self, details: Dict[str, Any]) -> Event:
		"""Create an event from a JSON object as returned by the Calendar API"""
		desc = details.get("description")
		return Event(
			event_id=details["id"],
			link=details["htmlLink"],
			title=details["summary"],
			all_day=("date" in details["start"]),
			location=details.get("location"),
			description=html_parser.html_links_to_md(desc) if desc else None,
			start=self.__get_endpoint_datetime(details, "start"),
			end=self.__get_endpoint_datetime(details, "end"),
		)

	def __get_endpoint_datetime(
		self, details: Dict[str, Any], endpoint: str
	) -> datetime:
		"""Returns a datetime given 'start' or 'end' as the endpoint"""
		dt = parse_date(
			details[endpoint].get("dateTime") or details[endpoint]["date"],
			from_tz=details[endpoint].get("timeZone") or self.timezone,
			to_tz=self.timezone,
		)
		assert dt is not None
		return dt