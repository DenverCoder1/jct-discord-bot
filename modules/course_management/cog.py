from typing import Optional
import discord
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from modules.course_management import util
from modules.course_management.util import sort_courses
from utils.embedder import embed_success
from discord.ext.commands import has_permissions
from discord.ext import commands
from utils.utils import get_discord_obj
from . import course_adder
from . import course_deleter
from . import course_activator
import config
from discord.ext import tasks


class CourseManagerCog(commands.Cog):
	@commands.Cog.listener()
	async def on_ready(self):
		self.sort_courses_categories.start()

	@cog_ext.cog_subcommand(
		base="course",
		name="add",
		description="Add a new course to the database and create a channel for it.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="course_name",
				description=(
					'The full name of the course. (eg. "Advanced Object Oriented'
					' Programming and Design")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=True,
			),
			create_option(
				name="professors",
				description=(
					"A comma separated string of names of professors who teach the"
					' course. (eg. "shahar golan, eitan")'
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
			create_option(
				name="channel_name",
				description=(
					"The name of the channel. (eg. object-oriented-programming)"
					" (default is course name)"
				),
				option_type=SlashCommandOptionType.STRING,
				required=False,
			),
		],
	)
	@has_permissions(manage_channels=True)
	async def add_course(
		self,
		ctx: SlashContext,
		course_name: str,
		professors: str = "",
		channel_name: Optional[str] = None,
	):
		await ctx.defer()
		professors_split = [professor.strip() for professor in professors.split(",")]
		if not channel_name:
			channel_name = course_name
		channel = await course_adder.add_course(
			ctx, course_name, professors_split, channel_name
		)
		await ctx.send(
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
	async def delete_course(self, ctx: SlashContext, channel: discord.TextChannel):
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
	async def activate_course(self, ctx: SlashContext, course: discord.TextChannel):
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
	async def deactivate_course(self, ctx: SlashContext, course: discord.TextChannel):
		await ctx.defer()
		await course_activator.deactivate_course(ctx, course)
		await ctx.send(embed=embed_success(f"Successfully deactivated #{course.name}."))

	@cog_ext.cog_subcommand(
		base="course",
		name="deactivate-all",
		description="Move all active course channels to the inactive courses list.",
		guild_ids=[config.guild_id],
		options=[],
	)
	@has_permissions(manage_channels=True)
	async def deactivate_all_courses(self, ctx: SlashContext):
		await ctx.defer()
		await course_activator.deactivate_all_courses(ctx)
		await ctx.send(embed=embed_success(f"Successfully deactivated all courses."))

	@cog_ext.cog_subcommand(
		base="course",
		name="sort",
		description="Sort all course channels alphabetically.",
		guild_ids=[config.guild_id],
	)
	@has_permissions(manage_channels=True)
	async def sort_courses(self, ctx: SlashContext):
		ctx.defer()
		await util.sort_courses()

	@tasks.loop(hours=24)
	async def sort_courses_categories(self):
		await util.sort_courses()


def setup(bot):
	bot.add_cog(CourseManagerCog())
