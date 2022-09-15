import asyncio
from database import preloaded
from database.campus import Campus
from utils import embedder, utils
from . import assigner
from nextcord.ext import commands
import nextcord
import config


class JoinCog(commands.Cog):
	"""Join command to get new users information and place them in the right roles"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.assigner = None



	@nextcord.slash_command("join", guild_ids=[config.guild_id])
	@commands.has_role(utils.get_id("UNASSIGNED_ROLE"))
	async def join(
		self,
		interaction: nextcord.Interaction,
		first_name: str,
		last_name: str,
		campus: int = nextcord.SlashOption(choices={
			campus.name:campus.id
			for campus in preloaded.campuses
		}),
		year: str = nextcord.SlashOption(choices=[str(i) for i in range(1, 5)]),
	):
		"""Join command to get new users' information and place them in the right roles.
		
			Args:
				first_name (str): Your first name.
				last_name (str): Your last name.
				campus (str): Your campus (Lev or Tal).
				year (int): The user's year.
		"""
		await interaction.response.defer()
		await assigner.assign(
			interaction.user,
			f"{first_name.title()} {last_name.title()}",
			int(campus),
			int(year),
		)
		await interaction.send(
			embeds=[
				embedder.embed_success(
					title=f"**{interaction.user.display_name}** used **/{interaction.application_command.name}**"
				)
			]
		)


# setup functions for bot
def setup(bot: commands.Bot):
	bot.add_cog(JoinCog(bot))
