from typing import Optional

import nextcord
from nextcord.ext import application_checks, commands

from .error_logger import ErrorLogger
from .friendly_error import FriendlyError
from .quiet_warning import QuietWarning


class ErrorHandler:
    """
    Class that handles raised exceptions
    """

    def __init__(self, error_logger: ErrorLogger) -> None:
        self.logger = error_logger

    async def handle(
        self,
        error: BaseException,
        message: Optional[nextcord.Message] = None,
        interaction: Optional[nextcord.Interaction[commands.Bot]] = None,
    ):
        """Given an error, will handle it appropriately"""
        error = getattr(error, "original", error)
        if isinstance(error, FriendlyError):
            await self.__handle_friendly(error, message)

        elif isinstance(error, QuietWarning):
            self.__handle_quiet_warning(error)

        else:
            self.logger.log_to_file(error, message)
            user_error, to_log = self.__user_error_message(error)
            if to_log:
                await self.logger.log_to_channel(error, message)
            if interaction is not None:
                friendly_err = FriendlyError(
                    user_error,
                    interaction,
                    interaction.user,
                    error,
                )
                await self.handle(friendly_err, interaction=interaction)
            elif message is not None:
                friendly_err = FriendlyError(
                    user_error,
                    message.channel,
                    message.author,
                    error,
                )
                await self.handle(friendly_err, message)

    async def __handle_friendly(
        self, error: FriendlyError, message: Optional[nextcord.Message] = None
    ):
        if error.inner:
            self.logger.log_to_file(error.inner, message)
        await error.reply()

    def __handle_quiet_warning(self, warning: QuietWarning):
        self.logger.log_to_file(warning)

    def __user_error_message(self, error: BaseException):
        """Given an error, will return a user-friendly string, and whether or not to log the error in the channel"""
        if isinstance(error, application_checks.ApplicationMissingPermissions):
            return (
                "You are missing the following permissions required to run the"
                " command:"
                f' {", ".join(str(perm) for perm in error.missing_permissions)}.',
                False,
            )
        elif isinstance(error, application_checks.ApplicationMissingRole):
            return f"You do not have the required role to run this command.", False
        elif isinstance(error, nextcord.ApplicationCheckFailure):
            return f"Error while executing the command.", True
        else:
            return f"An unknown error occurred.", True
