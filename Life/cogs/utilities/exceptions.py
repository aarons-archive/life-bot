
class LifeError(Exception):
    """Base exception for errors within the Life bot."""

class BotNotReadyError(LifeError):
    """Raised when an error occurs because the bot is not ready yet."""

class ArgumentError(LifeError):
    """Raised when an argument errors."""

class LifeVoiceError(LifeError):
    """Base exception for errors in the Life voice cog."""

class LifePlaylistError(LifeError):
    """Base exception for errors in the Life playlist cog."""
    

