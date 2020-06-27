from discord import Permissions


class Guild:

    def __init__(self, data: dict):
        self.data = data

        self.id = int(data.get('id'))
        self.name = data.get('name')
        self.icon_hash = data.get('icon')
        self.owner = data.get('owner')
        self.permissions = Permissions(data.get('permissions'))
        self.features = data.get('features')

    @property
    def icon(self):
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon_hash}.png?size=512'


class User:

    def __init__(self, data: dict):
        self.data = data

        self.id = int(data.get('id'))
        self.username = data.get('username')
        self.discriminator = data.get('discriminator')
        self.avatar_hash = data.get('avatar')
        self.bot = data.get('bot')
        self.system = data.get('system')
        self.mfa_enabled = data.get('mfa_enabled')
        self.locale = data.get('locale')
        self.flags = data.get('flags')
        self.premium_type = data.get('premium_type')
        self.public_flags = data.get('public_flags')

    @property
    def avatar(self):
        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}.png?size=512'

    @property
    def name(self):
        return f'{self.username}#{self.discriminator}'

