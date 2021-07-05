"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import enum


class Environment(enum.Enum):
    PROD = 'prod'
    DEV = 'dev'


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


class EmbedSize(enum.Enum):
    LARGE = 0
    MEDIUM = 1
    SMALL = 2


class ReminderRepeatType(enum.Enum):
    NEVER = 0

    EVERY_HALF_HOUR = 1
    EVERY_HOUR = 2
    EVERY_OTHER_HOUR = 3
    BI_HOURLY = EVERY_OTHER_HOUR

    EVERY_HALF_DAY = 4
    EVERY_DAY = 5
    EVERY_OTHER_DAY = 6
    BI_DAILY = EVERY_OTHER_DAY

    EVERY_WEEK = 7
    EVERY_OTHER_WEEK = 8
    EVERY_FORTNIGHT = EVERY_OTHER_WEEK
    BI_WEEKLY = EVERY_OTHER_WEEK

    EVERY_HALF_MONTH = 9
    EVERY_MONTH = 10
    EVERY_OTHER_MONTH = 11
    BI_MONTHLY = EVERY_OTHER_MONTH

    EVERY_HALF_YEAR = 12
    EVERY_YEAR = 13
    EVERY_OTHER_YEAR = 14
    BI_YEARLY = EVERY_OTHER_YEAR

    EVERY_30_SECONDS = 15


class EnabledFilters(enum.Enum):
    ROTATION = 0
    NIGHTCORE = 1
