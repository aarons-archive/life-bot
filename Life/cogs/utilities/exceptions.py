"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""

from discord.ext import commands


class LifeError(commands.CommandError):
    pass


class ArgumentError(LifeError):
    pass


class LifeImageError(LifeError):
    pass


class LifeVoiceError(LifeError):
    pass


class LifePlaylistError(LifeError):
    pass


class LifeHTTPError(LifeError):
    pass


class LifeHTTPForbidden(LifeError):
    pass


class LifeHTTPNotFound(LifeError):
    pass
