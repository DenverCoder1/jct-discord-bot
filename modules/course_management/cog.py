from typing import Optional
import nextcord
from nextcord import SlashOption
from modules.course_management import util
from utils.embedder import embed_success
from nextcord.ext.commands import has_permissions
from nextcord.ext import commands
from . import course_adder
from . import course_deleter
from . import course_activator
import config
from nextcord.ext import tasks


class CourseManagerCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.sort_courses_categories.start()
		self.bot = bot

	@nextcord.slash_command(guild_ids=[config.guild_id])
	async def course(self, interaction: nextcord.Interaction[commands.Bot]):
		"""This is a base command for all course commands and is not invoked"""
		pass

	@course.subcommand(name="add")
	@has_permissions(manage_channels=True)
	async def add_course(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		course_name: str,
		channel_name: str,
		professors: str = "",
	):
		"""Add a new course to the database and create a channel for it.
		
		Args:
			course_name: The full name of the course. (eg. "Advanced Object Oriented Programming and Design")
			channel_name: The name of the channel. (eg. object-oriented-programming) (default is course name)
			professors: A comma separated string of names of professors who teach the course. (eg. "shahar golan, eitan")
		"""
		await interaction.response.defer()
		professors_split = [professor.strip() for professor in professors.split(",")]
		if not channel_name:
			channel_name = course_name
		channel = await course_adder.add_course(
			interaction, course_name, professors_split, channel_name
		)
		await interaction.send(
			embed=embed_success("Nice! You created a course channel.", channel.mention)
		)

	@course.subcommand(name="delete")
	@has_permissions(manage_channels=True)
	async def delete_course(
		self, interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel
	):
		"""Delete course from the database and delete its channel. (For discontinued courses).

		Args:
			channel: The channel corresponding to the course you want to delete.
		"""
		await interaction.response.defer()
		await course_deleter.delete_course(interaction, channel)
		await interaction.send(
			embed=embed_success(
				"Well done... All evidence of that course has been deleted from the"
				" face of the earth. Hope you're proud of yourself."
			)
		)

	@course.subcommand(name="activate")
	@has_permissions(manage_channels=True)
	async def activate_course(
		self, interaction: nextcord.Interaction[commands.Bot], course: nextcord.TextChannel
	):
		"""Move an inactive course channel to the active courses list.

		Args:
			course: The channel corresponding to the course you want to activate.
		"""
		await interaction.response.defer()
		await course_activator.activate_course(interaction, course)
		await interaction.send(embed=embed_success(f"Successfully activated #{course.name}."))

	@course.subcommand(name="deactivate")
	@has_permissions(manage_channels=True)
	async def deactivate_course(self, interaction: nextcord.Interaction[commands.Bot], course: nextcord.TextChannel):
		"""Move an active course channel to the inactive courses list.

		Args:
			course: The channel corresponding to the course you want to deactivate.
		"""
		await interaction.response.defer()
		await course_activator.deactivate_course(interaction, course)
		await interaction.send(embed=embed_success(f"Successfully deactivated #{course.name}."))

	@course.subcommand(name="deactivate-all")
	@has_permissions(manage_channels=True)
	async def deactivate_all_courses(self, interaction: nextcord.Interaction[commands.Bot]):
		"""Move all active course channels to the inactive courses list."""
		await interaction.response.defer()
		await course_activator.deactivate_all_courses(interaction)
		await interaction.send(embed=embed_success("Successfully deactivated all courses."))

	@course.subcommand(name="sort")
	@has_permissions(manage_channels=True)
	async def sort_courses(self, interaction: nextcord.Interaction[commands.Bot]):
		"""Sort all course channels alphabetically."""
		await interaction.response.defer()
		await util.sort_courses()
		await interaction.send(
			embed=embed_success(
				"I'm pretty bad at sorting asynchronously, but I think I did it"
				" right..."
			)
		)

	@tasks.loop(hours=24)
	async def sort_courses_categories(self):
		await util.sort_courses()

	@sort_courses_categories.before_loop
	async def before_sort(self):
		await self.bot.wait_until_ready()


def setup(bot):
	bot.add_cog(CourseManagerCog(bot))
