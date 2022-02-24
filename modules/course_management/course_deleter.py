import nextcord
from modules.course_management.util import is_course
from ..error.friendly_error import FriendlyError
from database import sql


async def delete_course(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
	await __delete_channel(ctx, channel)
	await __delete_from_database(channel.id)


async def __delete_channel(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
	if is_course(channel):
		await channel.delete()
	else:
		raise FriendlyError(
			"You must provide a channel in the (active or inactive) courses category.",
			ctx,
			ctx.author,
		)


async def __delete_from_database(channel_id: int):
	await sql.delete("categories", channel=channel_id)