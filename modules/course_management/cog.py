from typing import Optional
import discord
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from utils.embedder import embed_success
from discord.ext.commands import has_permissions
from discord.ext import commands
from . import course_adder
from . import course_deleter
from . import course_activator
import config


class CourseManagerCog(commands.Cog):
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
		await course_deleter.delete_course(ctx, channel.id)
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
		await course_activator.activate_course(ctx, course.id)
		await ctx.send(embed=embed_success(f"Successfully activated {course.name}."))


def setup(bot):
	bot.add_cog(CourseManagerCog())
