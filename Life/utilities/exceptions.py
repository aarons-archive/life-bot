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
import discord
from discord.ext import commands


class LifeError(commands.CommandError):
    pass


class ArgumentError(LifeError):
    pass


class ImageError(LifeError):
    pass


class VoiceError(LifeError):
    pass


class GeneralError(LifeError):
    pass


class EmbedError(LifeError):

    def __init__(self, embed: discord.Embed) -> None:
        self._embed: discord.Embed = embed

    @property
    def embed(self) -> discord.Embed:
        return self._embed
