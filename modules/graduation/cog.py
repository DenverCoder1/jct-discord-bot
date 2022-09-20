from modules.graduation import graduation
from nextcord.ext import commands
from utils.scheduler import Scheduler


class GraduationCog(commands.Cog):
	"""Performs the required housekeeping when a class graduates."""

	@Scheduler.schedule()
	async def on_winter_semester_start(self):
		groups = await graduation.get_graduating_groups()
		await graduation.add_alumni_role(groups)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(GraduationCog())
