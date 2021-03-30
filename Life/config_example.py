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

# Bot
TOKEN = ''
PREFIX = ''
CLIENT_ID = ''
EXTENSIONS = [
    'jishaku',
    'cogs.dev',
    'cogs.todo',
    'cogs.tags',
    'cogs.time',
    'cogs.kross',
    'cogs.images',
    'cogs.config',
    'cogs.events',
    'cogs.economy',
    'cogs.birthdays',
    'cogs.information',
    'cogs.voice.music',
    'cogs.voice.radio',
    'cogs.systemcollapse',
]
OWNER_IDS = {
    0
}


# Tokens
AXEL_WEB_TOKEN = ''
KSOFT_TOKEN = ''
WOLFRAM_ALPHA_TOKEN = ''
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''


# Connection information
POSTGRESQL = {
    'host':     '',
    'user':     '',
    'database': '',
    'password': '',
}
REDIS = {
    'host':     '',
    'port':     0,
    'password': '',
    'db':       0,
}
NODES = [
    {
        'host':       '',
        'port':       '',
        'identifier': '',
        'password':   '',
        'type':       '',
    },
    {
        'host':       '',
        'port':       '',
        'identifier': '',
        'password':   '',
        'type':       '',
    },
]
WEB_ADDRESS = '127.0.0.1'
WEB_PORT = 8080
WEB_URL = f'{WEB_ADDRESS}:{WEB_PORT}'
SPOTIFY_CALLBACK_URI = 'http://127.0.0.1'


# Webhook URL's
ERROR_WEBHOOK_URL = ''
LOGGING_WEBHOOK_URL = ''
DM_WEBHOOK_URL = ''
