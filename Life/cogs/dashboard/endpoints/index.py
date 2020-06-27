from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint


class Index(BaseEndpoint, ABC):

    async def get(self):
        return await self.render('index.html', bot=self.bot, user=await self.get_user())


def setup(**kwargs):
    return r'/', Index, kwargs
