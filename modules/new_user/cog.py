from .greeter import Greeter
import discord
from discord.ext import commands
import config


class NewUserCog(commands.Cog):
	"""Ask members who join to use the join command"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.greeter = Greeter(bot)

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		"""Ask members who join to use the join command."""

		# if joined a different guild, skip welcoming
		if member.guild != config.guild():
			return

		print(f"{member.name} joined the server.")

		await self.greeter.give_initial_role(member)

		if not member.bot:
			await self.greeter.server_greet(member)
			await self.greeter.private_greet(member)


# setup functions for bot
def setup(bot):
	bot.add_cog(NewUserCog(bot))
