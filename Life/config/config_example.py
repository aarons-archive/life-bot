from cogs.dashboard.endpoints import main, dashboard, metrics, player_api


class LifeConfig:

    def __init__(self):

        self.token = ''
        self.prefix = ''

        self.idevision_key = ''
        self.spotify_app_id = ''
        self.spotify_secret = ''

        self.owner_ids = {}

        self.extensions = [
            'jishaku', 'cogs.dev', 'cogs.todo', 'cogs.tags', 'cogs.images', 'cogs.config', 'cogs.events', 'cogs.information', 'cogs.voice.music',
            'cogs.dashboard.dashboard', 'cogs.prometheus',
        ]

        self.nodes = {
            'MAIN': {'host': '',
                     'port': '',
                     'identifier': 'MAIN',
                     'password': ''
                     },
        }

        self.postgresql = {
            'host': '',
            'user': '',
            'database': '',
            'password': '',
        }

        self.redis = {
            'host': '',
            'port': 00000,
            'password': '',
            'db': 0,
        }

        self.ip = f''
        self.port = 00000

        self.endpoints = [main, dashboard, metrics, player_api]

        self.client_id = ''
        self.client_secret = ''

        self.login_redirect_uri = ''
        self.redirect_uri = f''

        self.cookie_secret = f''
