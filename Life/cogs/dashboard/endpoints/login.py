from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint


class Login(BaseEndpoint, ABC):

    async def get(self):
        return self.redirect('https://discord.com/api/oauth2/authorize?client_id=628284183579721747&redirect_uri=http'
                             '%3A%2F%2F192.168.0.26%3A8080%2Fsuccess&response_type=code&scope=identify%20guilds')


def setup(**kwargs):
    return r'/login', Login, kwargs

