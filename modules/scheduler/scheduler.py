import threading
import datetime as dt
from .func_instance import FuncInstance
from pyluach import dates


class Scheduler:
	events = {
		"on_new_academic_year": [],
	}

	@staticmethod
	def schedule(func):
		"""
		Use the decorator @Scheduler.schedule to make your function run at certain events.
		Available events are:
		- on_new_academic_year
		"""

		def wrapper(*args, **kwargs):
			Scheduler.events[func.__name__].append(FuncInstance(func, args, kwargs))

		return wrapper

	def __init__(self) -> None:
		self.__await_new_academic_year()

	def __await_new_academic_year(self):
		now = dt.datetime.now()
		h_year = dates.HebrewDate.today().year
		h_trigger_date = dates.HebrewDate(h_year, 5, 26)

		# the datetime when new academic year should be triggered
		dt_trigger = dt.datetime.combine(h_trigger_date.to_pydate(), dt.time(16))

		# if we're past dt_trigger but before Rosh Hashana change trigger to next year
		if now > dt_trigger:
			h_trigger_date = dates.HebrewDate(h_year + 1, 5, 26)
			dt_trigger = dt.datetime.combine(h_trigger_date.to_pydate(), dt.time(16))

		secs = (dt_trigger - now).total_seconds()
		threading.Timer(
			secs,
			self.__trigger_event,
			args=("on_new_academic_year", self.__await_new_academic_year),
		)

	def __trigger_event(self, name: str, on_complete):
		for instance in Scheduler.events[name]:
			instance.func(*instance.args, **instance.kwargs)
		on_complete()