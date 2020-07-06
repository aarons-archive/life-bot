from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint
import prometheus_client


class Metrics(BaseEndpoint, ABC):

    async def get(self):

        output = prometheus_client.generate_latest(prometheus_client.REGISTRY)
        self.write(output)


def setup(**kwargs):
    return r'/metrics', Metrics, kwargs



