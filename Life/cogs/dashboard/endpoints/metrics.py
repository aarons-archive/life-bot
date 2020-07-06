from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint


class Metrics(BaseEndpoint, ABC):

    async def get(self):

        message = []
        for event, count in self.bot.socket_stats.items():
            message.append(f'{event} {count}')
        self.write('\n'.join(message))


def setup(**kwargs):
    return r'/metrics', Metrics, kwargs



