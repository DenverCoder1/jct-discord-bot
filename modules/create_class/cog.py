from .class_channel_creator import ClassChannelCreator
from .class_creator import classes_creator
from utils.scheduler.scheduler import Scheduler
from utils.sql_fetcher import SqlFetcher
from utils import utils
from discord.ext import commands
import datetime
import os
import config


class CreateClassCog(commands.Cog, name="Year Roles"):
	"""Creates roles for each year and campus."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		sql_fetcher = config.sql_fetcher
		self.classes_creator = classes_creator(config.conn, sql_fetcher)

	@Scheduler.schedule()
	async def on_new_academic_year(self):
		"""Create roles for lev and tal of the new year."""
		year = datetime.datetime.now().year + 3
		# Create class objects for each campus of the new year
		classes = await self.classes_creator.create_classes(year)
		# Create a channel for all the classes of the new year
		await ClassChannelCreator.create_class_channel(f"🧮{year}-all", classes)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(CreateClassCog(bot))
