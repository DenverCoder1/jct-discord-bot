from modules.new_user.greeter import Greeter
import discord
import utils.utils as utils
from discord.ext import commands


class NewUserCog(commands.Cog, name="New User"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		guild = bot.get_guild(utils.get_id("JCT_GUILD_ID"))
		self.greeter = Greeter(guild.get_channel("INTRO_CHANNEL"))

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		"""Ask members who join to use the join command."""
		print(f"{member.name} joined the server.")

		await self.greeter.give_initial_role(member)

		if not member.bot:
			await self.greeter.server_greet(member)
			await self.greeter.private_greet(member)


# setup functions for bot
def setup(bot):
	bot.add_cog(NewUserCog(bot))