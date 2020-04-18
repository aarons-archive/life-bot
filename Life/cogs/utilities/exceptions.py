

class LifeError(Exception):
    """Base exception for errors within the Life bot."""


class BotNotReadyError(LifeError):
    """Raised when an error occurs because the bot is not ready yet."""
    
    
class ArgumentError(LifeError):
    """Raised when an argument errors."""


class LifeVoiceError(LifeError):
    """Base exception for Life Voice module errors."""
    
    
class NoTracksFound(LifeVoiceError):
    """Raised when a search for tracks return nothing."""
    

class NoTracksToRemove(LifeVoiceError):
    """Raised when there are no tracks in a playlist to remove based on a search."""
    

