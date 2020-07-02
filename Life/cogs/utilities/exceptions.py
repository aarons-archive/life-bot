"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""


class LifeError(Exception):
    """Base exception for errors within the Life bot."""


class ArgumentError(LifeError):
    """Raised when an argument errors."""


class LifeVoiceError(LifeError):
    """Base exception for errors in the Life voice cog."""


class LifePlaylistError(LifeError):
    """Base exception for errors in the Life playlist cog."""


class LifeHTTPError(LifeError):
    """Raised when making a request failed."""


class LifeHTTPForbidden(LifeError):
    """Raised when a HTTP request is forbidden."""


class LifeHTTPNotFound(LifeError):
    """Raised when a HTTP request doesn't find anything."""
