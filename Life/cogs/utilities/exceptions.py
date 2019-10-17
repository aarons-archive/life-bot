from discord.ext import commands


class MrBotError(commands.CommandError):
    """Base class for other exceptions"""
    pass


class WrongGuild(MrBotError):
    """Raised when a command is used in the wrong guild."""
    pass
