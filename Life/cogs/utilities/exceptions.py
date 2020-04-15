

class LifeError(Exception):
    """Base exception for errors within the Life bot."""


class ArgumentError(LifeError):
    """Raised when an argument errors."""


class LifeVoiceError(LifeError):
    """Base exception for Life Voice module errors."""
    
    
class NoTracksFound(LifeVoiceError):
    """Raised when a search for tracks return nothing."""
