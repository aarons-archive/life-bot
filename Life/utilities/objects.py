"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord


class DefaultGuildConfig:

    __slots__ = ('prefixes', 'colour')

    def __init__(self) -> None:

        self.prefixes = []
        self.colour = discord.Colour.gold()

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig prefixes={self.prefixes} colour={self.colour}>'


class GuildConfig:

    __slots__ = ('prefixes', 'colour')

    def __init__(self, data: dict) -> None:

        self.prefixes = data.get('prefixes')
        self.colour = discord.Colour(int(data.get('colour'), 16))

    def __repr__(self) -> str:
        return f'<GuildConfig prefixes={self.prefixes} colour={self.colour}>'


class DefaultUserConfig:

    __slots__ = 'colour'

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()

    def __repr__(self) -> str:
        return f'<DefaultUserConfig colour={self.colour}>'


class UserConfig:

    __slots__ = 'colour'

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))

    def __repr__(self) -> str:
        return f'<UserConfig colour={self.colour}>'

