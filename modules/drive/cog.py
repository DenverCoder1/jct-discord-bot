import nextcord
from nextcord.ext import commands

import config
from modules.drive.drive_service import DriveService
from utils.embedder import embed_success
from utils.utils import is_email

from ..error.friendly_error import FriendlyError


class DriveCog(commands.Cog):
    """Display and update Google Drive events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.service = DriveService(folder_id=config.drive_folder_id)

    @nextcord.slash_command(guild_ids=[config.guild_id])
    async def drive(self, interaction: nextcord.Interaction[commands.Bot]):
        """This is a base command for all Drive commands and is not invoked"""
        pass

    @drive.subcommand(name="link")
    async def drive_link(self, interaction: nextcord.Interaction[commands.Bot]):
        """Get the link to view the ESP Google Drive folder"""
        folder_link = f"https://drive.google.com/drive/u/0/folders/{config.drive_folder_id}"
        await interaction.send(
            embed=embed_success(
                title=":link: Google Drive Link",
                description=(
                    f"<:google_drive:785981940289372170> [Computer Science Resources JCT ESP All Courses]({folder_link})\n\n"
                    f"Use the {self.drive_grant.get_mention(interaction.guild)} command to add yourself as a manager of the Google Drive."
                ),
                url=folder_link,
            )
        )

    @drive.subcommand(name="grant")
    async def drive_grant(self, interaction: nextcord.Interaction[commands.Bot], email: str):
        """Add a Google account as a manager of the ESP Google Drive

        Args:
            email: The email address of the Google account to add
        """
        await interaction.response.defer(ephemeral=True)
        # validate email address
        if not is_email(email):
            raise FriendlyError(
                "Invalid email address",
                interaction,
                interaction.user,
                ephemeral=True,
            )
        # add manager to Drive
        if self.service.add_manager(email):
            embed = embed_success(
                title=f":office_worker: Successfully added {email} as an editor to the ESP Google Drive.",
                description=(
                    f"Thanks for helping keep the Drive up to date! :heart:\n\n"
                    f"You now have access to upload any tests, assignments, or other documents that may be useful to other students.\n\n"
                    f"Please read through the [Drive Guidelines]({config.drive_guidelines_url}) for more information on keeping the Drive organized."
                ),
            )
            if email.endswith("@g.jct.ac.il"):
                embed.description = (
                    f"{embed.description}\n\n"
                    ":warning: Note: This is a JCT email address, since it is unclear whether this email address is permanent, "
                    "we recommend that you use a personal email address instead to avoid files potentially being lost in the future."
                )
            await interaction.send(embed=embed, ephemeral=True)
            return
        raise FriendlyError(
            "An error occurred while applying changes.",
            interaction,
            interaction.user,
            ephemeral=True,
        )


# setup functions for bot
def setup(bot):
    bot.add_cog(DriveCog(bot))
