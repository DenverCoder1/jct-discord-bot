import asyncio
import datetime as dt
import threading
from typing import Dict

from nextcord.ext import commands
from pyluach import dates

from .event import Event
from .func_instance import FuncInstance


class Scheduler:
    events: Dict[str, Event] = {
        "on_new_academic_year": Event(),
        "on_winter_semester_start": Event(),
    }

    @staticmethod
    def schedule(dependency_index: int = 0):
        """
        Use the decorator @Scheduler.schedule() to make your function run at certain events.
        If you require your function to run after any other which is also scheduled for the same event, pass an use @Scheduler.schedule(n) where n is greater than the number passed to the scheduler for the function which yours depends on (default is 0).

        Available events are:
        - on_new_academic_year
        - on_winter_semester_start

        Note: You must name the function the same as the event name.
        """

        def decorator(func):
            Scheduler.events[func.__name__].add_function(FuncInstance(func), dependency_index)
            return func

        return decorator

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.__await_new_academic_year()
        self.__await_winter_semester_start()

    def __await_new_academic_year(self):
        """Event that will run every year on Av 26 at 4pm"""
        secs = self.__secs_to_heb_date(5, 26, 16)
        self.__await_event(secs, "on_new_academic_year", self.__await_new_academic_year)

    def __await_winter_semester_start(self):
        """Event that will run every year on Tishri 18 at 4pm"""
        secs = self.__secs_to_heb_date(7, 18, 16)
        self.__await_event(secs, "on_winter_semester_start", self.__await_winter_semester_start)

    def __await_event(self, secs: float, event_name: str, on_complete):
        if threading.TIMEOUT_MAX > secs:
            threading.Timer(
                secs,
                asyncio.run_coroutine_threadsafe,
                args=(
                    self.__trigger_event(event_name, on_complete),
                    asyncio.get_running_loop(),
                ),
            ).start()

    def __secs_to_heb_date(
        self, h_month: int, h_day: int, hour: int = 0, min: int = 0, sec: int = 0
    ):
        """Returns the number of seconds from now until the next time a hebrew date occurs"""
        now = dt.datetime.now()
        h_year = dates.HebrewDate.today().year
        h_trigger_date = dates.HebrewDate(h_year, h_month, h_day)

        # the datetime when new academic year should be triggered
        dt_trigger = dt.datetime.combine(h_trigger_date.to_pydate(), dt.time(hour, min, sec))

        # if we're past dt_trigger but before Rosh Hashana change trigger to next year
        if now > dt_trigger:
            h_trigger_date = dates.HebrewDate(h_year + 1, h_month, h_day)
            dt_trigger = dt.datetime.combine(h_trigger_date.to_pydate(), dt.time(hour, min, sec))

        return (dt_trigger - now).total_seconds()

    async def __trigger_event(self, name: str, on_complete):
        print(f"Triggering event: {name}")
        await Scheduler.events[name].fire(self.bot)
        on_complete()
