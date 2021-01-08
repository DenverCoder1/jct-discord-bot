from modules.admin_symbol.admin_symbol import is_admin, add_symbol, remove_symbol
from discord.ext import commands

class AdminSymbol(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		print('member updated')
		print(before.nick)
		print(after.nick)

		admin_before = is_admin(before)
		admin_now = is_admin(after)

		if not admin_before and admin_now:
			await add_symbol(after)
		elif admin_before and not admin_now:
			await remove_symbol(after)


def setup(bot):
	bot.add_cog(AdminSymbol(bot))