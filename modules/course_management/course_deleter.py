import nextcord
from modules.course_management.util import is_course
from ..error.friendly_error import FriendlyError
from database import sql
from nextcord.ext import commands


async def delete_course(
	interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel
):
	await __delete_channel(interaction, channel)
	await __delete_from_database(channel.id)


async def __delete_channel(
	interaction: nextcord.Interaction[commands.Bot], channel: nextcord.TextChannel
):
	if is_course(channel):
		await channel.delete()
	else:
		raise FriendlyError(
			"You must provide a channel in the (active or inactive) courses category.",
			interaction,
			interaction.user,
		)


async def __delete_from_database(channel_id: int):
	await sql.delete("categories", channel=channel_id)