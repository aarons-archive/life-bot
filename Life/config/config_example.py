from cogs.dashboard.endpoints import main, dashboard, metrics, websocket


class LifeConfig:

    def __init__(self):

        self.token = 'NzQ3MDQzMDM2MjUyMzQwMjM1.X0JICw.-kkhfzvSx0KWsX3z3WstRdom1pA'
        self.prefix = '-'

        self.idevision_key = ''
        self.spotify_app_id = '9ec5ff63926240ef90a6266c9a18112f'
        self.spotify_secret = '3ba8e5bc20c148468d4eb3dfdd3578da'

        self.owner_ids = {522714407969488896}

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
            'host': 'ec2-54-247-103-43.eu-west-1.compute.amazonaws.com',
            'user': 'lqkvopxounxtap',
            'database': 'dfuf4b4t6q8n38',
            'password': 'b601ae4959b8adc77f0221e5c2d9dd287cab0a37f4d5cd4ef57db84b1a70887b',
        }

        self.redis = {
            'host': 'ec2-54-155-29-250.eu-west-1.compute.amazonaws.com',
            'port': 14179,
            'password': 'p6baba6058ea3a90a8efb7a8005e379462c838936f2826f43bc7737e6f5180a9d',
            'db': h,
        }

        self.ip = ''
        self.port = 00000

        self.endpoints = [main, dashboard, metrics, websocket]

        self.client_id = ''
        self.client_secret = ''

        self.login_redirect_uri = ''
        self.redirect_uri = ''

        self.cookie_secret = ''
