#  Lif
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

import enum


class Operation(enum.Enum):

    SET = 'set'
    UPDATE = SET

    RESET = 'reset'

    ADD = 'add'
    PLUS = ADD

    MINUS = 'remove'
    REMOVE = MINUS


class Updateable(enum.Enum):

    COINS = 'coins'
    XP = 'xp'

    DAILY_COLLECTED = 'daily_collected'
    WEEKLY_COLLECTED = 'weekly_collected'
    MONTHLY_COLLECTED = 'monthly_collected'

    DAILY_STREAK = 'daily_streak'
    WEEKLY_STREAK = 'weekly_streak'
    MONTHLY_STREAK = 'monthly_streak'


class EmbedSize(enum.Enum):

    LARGE = 0
    MEDIUM = 1
    SMALL = 2


