#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from discord.ext import commands


class LifeError(commands.CommandError):
    pass


class ArgumentError(LifeError):
    pass


class ImageError(LifeError):
    pass


class VoiceError(LifeError):
    pass


class HTTPError(LifeError):
    pass


class HTTPForbidden(LifeError):
    pass


class HTTPNotFound(LifeError):
    pass
