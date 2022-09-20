from typing import Optional
from nextcord.ext import commands
from modules.markdown import tip_formatter
import config
import nextcord


class FormattingCog(commands.Cog):
	"""Display markdown tips for Discord messages"""

	def __init__(self, bot):
		self.bot = bot

	@nextcord.slash_command(name="markdown", guild_ids=[config.guild_id])
	async def markdown(
		self,
		interaction: nextcord.Interaction[commands.Bot],
		format: Optional[str] = nextcord.SlashOption(
			choices={
				tip_formatter.formats[key].name: key for key in tip_formatter.formats
			}
		),
	):
		"""Command to display markdown tips for Discord messages.

		Args:
			format (str): The format to display information about (default is all).
		"""
		if not format:
			message = tip_formatter.all_markdown_tips()
		else:
			message = tip_formatter.individual_info(format)
		await interaction.send(message)


# setup functions for bot
def setup(bot):
	bot.add_cog(FormattingCog(bot))
