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

	@nextcord.slash_command(description="Course group", guild_ids=[config.guild_id])
	def course(self, interaction: nextcord.Interaction):
		"""This is a base command for all course commands and is not invoked"""
		pass

	@course.subcommand(
		name="add",
		description="Add a new course to the database and create a channel for it.",
	)
	@has_permissions(manage_channels=True)
	async def add_course(
		self,
		interaction: nextcord.Interaction,
		course_name: str = SlashOption(
			description='The full name of the course. (eg. "Advanced Object Oriented Programming and Design")'
		),
		professors: str = SlashOption(
			description='A comma separated string of names of professors who teach the course. (eg. "shahar golan, eitan")',
			default="",
		),
		channel_name: str = SlashOption(
			description="The name of the channel. (eg. object-oriented-programming) (default is course name)",
		),
	):
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

	@cog_ext.cog_subcommand(
		base="course",
		name="delete",
		description=(
			"Delete course from the database and delete its channel. (For discontinued"
			" courses)."
		),
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="course",
				description=(
					"The channel corresponding to the course you want to delete."
				),
				option_type=SlashCommandOptionType.CHANNEL,
				required=True,
			),
		],
		connector={"course": "channel"},
	)
	@has_permissions(manage_channels=True)
	async def delete_course(
		self, interaction: nextcord.Interaction, channel: nextcord.TextChannel
	):
		await ctx.defer()
		await course_deleter.delete_course(ctx, channel)
		await ctx.send(
			embed=embed_success(
				"Well done... All evidence of that course has been deleted from the"
				" face of the earth. Hope you're proud of yourself."
			)
		)

	@cog_ext.cog_subcommand(
		base="course",
		name="activate",
		description="Move an inactive course channel to the active courses list.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="course",
				description=(
					"The channel corresponding to the course you want to activate."
				),
				option_type=SlashCommandOptionType.CHANNEL,
				required=True,
			)
		],
	)
	async def activate_course(
		self, interaction: nextcord.Interaction, course: nextcord.TextChannel
	):
		await ctx.defer()
		await course_activator.activate_course(ctx, course)
		await ctx.send(embed=embed_success(f"Successfully activated #{course.name}."))

	@cog_ext.cog_subcommand(
		base="course",
		name="deactivate",
		description="Move an active course channel to the inactive courses list.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="course",
				description=(
					"The channel corresponding to the course you want to deactivate."
				),
				option_type=SlashCommandOptionType.CHANNEL,
				required=True,
			)
		],
	)
	@has_permissions(manage_channels=True)
	async def deactivate_course(
		self, interaction: nextcord.Interaction, course: nextcord.TextChannel
	):
		await ctx.defer()
		await course_activator.deactivate_course(ctx, course)
		await ctx.send(embed=embed_success(f"Successfully deactivated #{course.name}."))

	@cog_ext.cog_subcommand(
		base="course",
		name="deactivate-all",
		description="Move all active course channels to the inactive courses list.",
		guild_ids=[config.guild_id],
	)
	@has_permissions(manage_channels=True)
	async def deactivate_all_courses(self, interaction: nextcord.Interaction):
		await ctx.defer()
		await course_activator.deactivate_all_courses(ctx)
		await ctx.send(embed=embed_success("Successfully deactivated all courses."))

	@cog_ext.cog_subcommand(
		base="course",
		name="sort",
		description="Sort all course channels alphabetically.",
		guild_ids=[config.guild_id],
	)
	@has_permissions(manage_channels=True)
	async def sort_courses(self, interaction: nextcord.Interaction):
		await ctx.defer()
		await util.sort_courses()
		await ctx.send(
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
