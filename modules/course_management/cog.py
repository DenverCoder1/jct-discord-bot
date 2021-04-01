from utils.utils import decode_mention
from utils.embedder import embed_success
from discord.ext.commands import has_permissions
from discord.ext import commands
from modules.course_management.course_adder import CourseAdder
from modules.course_management.course_deleter import CourseDeleter
from modules.error.friendly_error import FriendlyError
import config


class CourseManagerCog(commands.Cog):
	def __init__(self):
		self.adder = CourseAdder(config.conn, config.sql_fetcher)
		self.deleter = CourseDeleter(config.conn, config.sql_fetcher)

	@has_permissions(manage_channels=True)
	@commands.command(name="courses.add")
	async def add_course(
		self,
		ctx: commands.Context,
		course_name: str,
		labels: str,
		professors: str,
		channel_name: str = "",
	):
		"""
		Add a new course to the database and create a channel for it.

		Usage:
		```
		++courses.add <course name> <labels> <professors> [channel name]
		```
		Arguments:
		**<course name>**: The full name of the course. (eg. "Advanced Object Oriented Programming and Design")
		**<labels>**: A space separated string of words associated with the course (eg. "oop aoopd java"). These can be used later to search for the course. No need to include words already in the course name.
		**<professors>**: A comma separated string of names of professors who teach the course. (eg. "shahar golan, eitan")
		**[channel name]**: The name of the channel. (eg. object-oriented-programming) (optional, default is course name)
		"""
		labels = labels.split()
		professors = [professor.strip() for professor in professors.split(",")]
		if channel_name == "":
			channel_name = course_name
		channel = await self.adder.add_course(
			ctx, course_name, labels, professors, channel_name
		)
		await ctx.send(
			embed=embed_success("Nice! You created a course channel.", channel.mention)
		)

	@has_permissions(manage_channels=True)
	@commands.command(name="courses.delete")
	async def delete_course(self, ctx: commands.Context, channel_mention: str):
		"""
		Delete course from the database and delete its channel. Note: This should only be done for a course that will never be taught again.

		Usage:
		```
		++courses.add <course mention>
		```
		Arguments:
		**<course mention>**: Mention the channel of the course you want to delete using #. (eg. #object-oriented-programming)
		"""
		mention_type, channel_id = decode_mention(channel_mention)
		if mention_type != "channel":
			raise FriendlyError(
				"Expected a channel mention.",
				description=(
					f"For example use ```\n{config.prefix}courses.delete"
					" #object-oriented-programming```"
				),
			)
		await self.deleter.delete_course(ctx, channel_id)
		await ctx.send(embed=embed_success("You successfully deleted the course."))


def setup(bot):
	bot.add_cog(CourseManagerCog())
