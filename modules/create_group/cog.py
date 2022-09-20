from . import group_channel_creator
from .group_creator import create_groups
from utils.scheduler import Scheduler
from nextcord.ext import commands
import datetime


class CreateGroupCog(commands.Cog):
	"""Creates roles for each year and campus."""

	@Scheduler.schedule()
	async def on_new_academic_year(self):
		"""Create roles for lev and tal of the new year."""
		year = datetime.datetime.now().year + 3
		# Create group objects for each campus of the new year
		groups = await create_groups(year)
		# Create a channel for all the groups of the new year
		await group_channel_creator.create_group_channel(
			f"🧮︱{year}-all",
			[group.role for group in groups],
			"Here you can discuss links and info relevant for students from all"
			" campuses in your year.",
		)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(CreateGroupCog())
