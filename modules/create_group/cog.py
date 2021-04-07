from .group_channel_creator import GroupChannelCreator
from .group_creator import groups_creator
from utils.scheduler import Scheduler
from discord.ext import commands
import datetime
import config


class CreateGroupCog(commands.Cog):
	"""Creates roles for each year and campus."""

	def __init__(self):
		self.groups_creator = groups_creator(config.conn)

	@Scheduler.schedule()
	async def on_new_academic_year(self):
		"""Create roles for lev and tal of the new year."""
		year = datetime.datetime.now().year + 3
		# Create group objects for each campus of the new year
		groups = await self.groups_creator.create_groups(year)
		# Create a channel for all the groups of the new year
		await GroupChannelCreator.create_group_channel(
			f"🧮{year}-all", [group.role for group in groups]
		)


# This function will be called when this extension is loaded. It is necessary to add these functions to the bot.
def setup(bot: commands.Bot):
	bot.add_cog(CreateGroupCog())
