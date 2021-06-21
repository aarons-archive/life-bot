import discord

from utilities.enums import Environment


ENV = Environment.DEV

TOKEN = 'BETA TOKEN' if ENV is Environment.DEV else 'MAIN TOKEN'
PREFIX = 'l_' if ENV is Environment.DEV else 'l-'


# Colours
MAIN = discord.Colour(0xF20034)
RED = discord.Colour(0xF21847)
YELLOW = discord.Colour(0xF2BA18)
GREEN = discord.Colour(0x18F23B)
BLUE = discord.Colour(0x0C3BF2)


# Values
ZWSP = '\u200b'
NL = '\n'


# Guild IDs
SUPPORT_SERVER_ID = 240958773122957312


# User IDs
OWNER_IDS = {
    238356301439041536
}


# Bot
EXTENSIONS = [
    'jishaku',

    'cogs.special.kross',
    'cogs.special.systemcollapse',

    'cogs.voice.play',
    'cogs.voice.player',
    'cogs.voice.queue',

    'cogs.birthdays',
    'cogs.dev',
    'cogs.economy',
    'cogs.events',
    'cogs.images',
    'cogs.information',
    'cogs.settings',
    'cogs.tags',
    'cogs.time',
    'cogs.todo',
]


# Connection information
POSTGRESQL = {
    'host':     '',
    'user':     '',
    'database': '',
    'password': '',
}

REDIS = ''

NODES = [
    {
        'host':       '',
        'port':       '20000',
        'identifier': 'ALPHA',
        'password':   '',
    },
    {
        'host':       '',
        'port':       '20001',
        'identifier': 'BRAVO',
        'password':   '',
    },
    {
        'host':       '',
        'port':       '20002',
        'identifier': 'CHARLIE',
        'password':   '',
    },
]


# Tokens
AXEL_WEB_TOKEN = ''
KSOFT_TOKEN = ''
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''


# Webhook URL's
ERROR_WEBHOOK_URL = ''
GUILD_WEBHOOK_URL = ''
DM_WEBHOOK_URL = ''
