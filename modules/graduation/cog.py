from modules.graduation.graduator import Graduator
from discord.ext import commands
from utils.scheduler.scheduler import Scheduler
import config


class GraduationCog(commands.Cog, name="Graduation"):
	"""Performs the required housekeeping when a class graduates."""

	def __init__(self):
		self.graduator = Graduator(config.conn, config.sql_fetcher, config.guild)

	@Scheduler.schedule()
	async def on_winter_semester_start(self):
		groups = self.graduator.get_graduating_groups()
		await self.graduator.add_alumni_role(groups)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(GraduationCog())