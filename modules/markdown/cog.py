from typing import Optional
from nextcord.ext import commands
from modules.markdown import tip_formatter
import config


class FormattingCog(commands.Cog):
	"""Display markdown tips for Discord messages"""

	def __init__(self, bot):
		self.bot = bot

	@cog_ext.cog_slash(
		name="markdown",
		description="Command to display markdown tips for Discord messages.",
		guild_ids=[config.guild_id],
		options=[
			create_option(
				name="format",
				description="The format to display information about (default is all)",
				option_type=SlashCommandOptionType.STRING,
				required=False,
				choices=[
					*[
						create_choice(name=tip_formatter.formats[key].name, value=key)
						for key in tip_formatter.formats
					]
				],
			),
		],
	)
	async def markdown(self, interaction: nextcord.Interaction, format: Optional[str] = None):
		if not format:
			message = tip_formatter.all_markdown_tips()
		else:
			message = tip_formatter.individual_info(format)
		await ctx.send(message)


# setup functions for bot
def setup(bot):
	bot.add_cog(FormattingCog(bot))