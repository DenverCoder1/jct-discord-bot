from modules.scheduler.scheduler import Scheduler
from discord.ext import commands


class SchedulerCog(commands.Cog, name="Scheduler"):
	"""Allows other cogs to subscribe to events such as new_academic_year"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.scheduler = Scheduler(bot)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(SchedulerCog(bot))