from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint


class Login(BaseEndpoint, ABC):

    async def get(self):
        return self.redirect(self.bot.config.DISCORD_LOGIN_URL)


def setup(**kwargs):
    return r'/login', Login, kwargs

