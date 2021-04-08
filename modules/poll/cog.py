import discord
from discord.ext import commands
from modules.poll.poll import Poll


class PollCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.polls = {}

	@commands.command(name="poll")
	async def poll(self, ctx, *args):
		""" A command to create new user polls """

		# Create the Poll object
		poll = Poll(ctx.message)

		# Send the poll to the chat and save it in the polls dict
		self.msg = await ctx.send(embed=poll.embed, delete_after=poll.duration)
		self.polls[self.msg] = poll

		# Add reaction voting options to the poll
		for i in range(len(poll.options)):
			await self.msg.add_reaction(poll.emojis[i])

		# delete the triggering message
		await ctx.message.delete()

	# TODO: This will have to be changed to on_raw_reaction_add because on_reaction_add only triggers for messages in the bot's cache
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
		if reaction.message in self.polls and not member.bot:
			# print(member.display_name + "added reaction")
			await self.polls[reaction.message].vote(reaction, member)

	# TODO: change to on_raw_reaction_remove, same reason as above
	@commands.Cog.listener()
	async def on_reaction_remove(
		self, reaction: discord.Reaction, member: discord.Member
	):
		if reaction.message in self.polls and not member.bot:
			# print(member.display_name + "removed reaction")
			await self.polls[reaction.message].unvote(reaction, member)


def setup(bot):
	bot.add_cog(PollCog(bot))
