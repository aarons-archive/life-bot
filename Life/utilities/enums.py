import enum


class Operations(enum.Enum):

    set = 'set'
    update = 'set'

    reset = 'reset'
    clear = 'reset'

    add = 'add'

    remove = 'remove'
    minus = 'remove'


class Editables(enum.Enum):

    colour = 'colour'

    prefixes = 'prefixes'

    timezone = 'timezone'
    timezone_private = 'timezone_private'

    blacklist = 'blacklist'

    coins = 'coins'
    xp = 'xp'

    level_up_notifications = 'level_up_notifications'

