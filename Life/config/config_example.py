

class LifeConfig:

    def __init__(self, bot):

        self.bot = bot

        self.token = ''
        self.prefix = ''

        self.spotify_app_id = ''
        self.spotify_secret = ''

        self.database_info = {
            'host': '',
            'user': '',
            'database': '',
            'password': '',
        }

        self.node_info = {
            'ALPHA': {
                'host': '',
                'port': '',
                'identifier': '',
                'password': ''
            },
        }

        self.extensions = [
            'jishaku',
            'cogs.dev',
            'cogs.todo',
            'cogs.images',
            'cogs.events',
            'cogs.information',
            'cogs.voice.music',
            'cogs.voice.events',
            'cogs.voice.playlists',
            'cogs.dashboard.dashboard'
        ]

        self.port = f''
        self.ip = f''

        self.client_id = f''
        self.client_secret = f''

        self.discord_login_url = f''

        self.discord_auth_url = f''
        self.cookie_secret = f''
