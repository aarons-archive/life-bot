from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint
import prometheus_client


class Metrics(BaseEndpoint, ABC):

    async def get(self):

        self.set_header(name='Content-Type', value=prometheus_client.CONTENT_TYPE_LATEST)
        return await self.finish(prometheus_client.generate_latest(prometheus_client.REGISTRY))


def setup(**kwargs):
    return [(r'/metrics', Metrics, kwargs)]



