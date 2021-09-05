# Future
from __future__ import annotations

# Packages
from discord.enums import Enum


class Environment(Enum):

    PRODUCTION = 1
    DEVELOPMENT = 2


class Operation(Enum):

    SET = 1
    RESET = 2

    APPEND = 3
    REMOVE = 4

    ADD = 5
    MINUS = 6


class EmbedSize(Enum):

    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class ReminderRepeatType(Enum):

    NEVER = 1

    EVERY_HALF_HOUR = 2
    EVERY_HOUR = 3
    EVERY_OTHER_HOUR = 4
    BI_HOURLY = EVERY_OTHER_HOUR

    EVERY_HALF_DAY = 5
    EVERY_DAY = 6
    EVERY_OTHER_DAY = 7
    BI_DAILY = EVERY_OTHER_DAY

    EVERY_WEEK = 8
    EVERY_OTHER_WEEK = 9
    EVERY_FORTNIGHT = EVERY_OTHER_WEEK
    BI_WEEKLY = EVERY_OTHER_WEEK

    EVERY_HALF_MONTH = 10
    EVERY_MONTH = 11
    EVERY_OTHER_MONTH = 12
    BI_MONTHLY = EVERY_OTHER_MONTH

    EVERY_HALF_YEAR = 13
    EVERY_YEAR = 14
    EVERY_OTHER_YEAR = 15
    BI_YEARLY = EVERY_OTHER_YEAR


class Filters(Enum):

    ROTATION = 1
    NIGHTCORE = 2
