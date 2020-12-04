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

class Config:

    def __init__(self, bot):
        self.bot = bot

        self.token = ''
        self.prefix = ''

        self.ksoft_token = ''
        self.wolframalpha_token = ''
        self.idevision_key = ''
        self.spotify_app_id = ''
        self.spotify_secret = ''

        self.errors_url = ''
        self.logging_url = ''
        self.mentions_dms_url = ''

        self.owner_ids = {}

        self.extensions = [
            'jishaku',
            'cogs.dev',
            'cogs.todo',
            'cogs.tags',
            'cogs.time',
            'cogs.images',
            'cogs.config',
            'cogs.events',
            'cogs.economy',
            'cogs.prometheus',
            'cogs.information',
            'cogs.voice.music',
            'cogs.systemcollapse',
            'cogs.dashboard.dashboard',
        ]

        self.nodes = [
            {'host': '',
                     'port': '',
                     'identifier': '',
                     'password': ''
             },
            {'host': '',
                     'port': '',
                     'identifier': '',
                     'password': ''
             }
        ]

        self.postgresql = {
            'host': '',
            'user': '',
            'database': '',
            'password': '',
        }

        self.redis = {
            'host': '',
            'port': 0,
            'password': '',
            'db': 0,
        }

        self.ip = ''
        self.port = 0

        self.client_id = ''
        self.client_secret = ''

        self.login_redirect_uri = f''
        self.redirect_uri = f''

        self.cookie_secret = ''
