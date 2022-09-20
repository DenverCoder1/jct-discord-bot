import nextcord
from nextcord.ext import application_checks, commands

import config
from database import preloaded
from utils import embedder, utils

from . import assigner


class JoinCog(commands.Cog):
    """Join command to get new users information and place them in the right roles"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.assigner = None

    @nextcord.slash_command("join", guild_ids=[config.guild_id])
    @application_checks.has_role(utils.get_id("UNASSIGNED_ROLE"))
    async def join(
        self,
        interaction: nextcord.Interaction[commands.Bot],
        first_name: str,
        last_name: str,
        campus: int = nextcord.SlashOption(
            choices={campus.name: campus.id for campus in preloaded.campuses}
        ),
        year: int = nextcord.SlashOption(choices={f"Year {i}": i for i in range(1, 5)}),
    ):
        """Join command to get new users' information and place them in the right roles.

        Args:
                first_name: Your first name.
                last_name: Your last name.
                campus: Your campus (Lev or Tal).
                year: Your year.
        """
        assert isinstance(
            interaction.user, nextcord.Member
        ), "Interaction user is not a guild member"
        await interaction.response.defer()
        await assigner.assign(
            interaction.user,
            f"{first_name.title()} {last_name.title()}",
            campus,
            year,
        )
        await interaction.send(
            embeds=[
                embedder.embed_success(
                    title=(
                        f"**{interaction.user.display_name}** used"
                        f" **/{interaction.application_command.name}**"
                    )
                )
            ]
        )


# setup functions for bot
def setup(bot: commands.Bot):
    bot.add_cog(JoinCog(bot))
