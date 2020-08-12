import asyncio
import datetime
import json
import weakref
from urllib.parse import quote

from utilities import exceptions


class Route:

    def __init__(self, method: str, endpoint: str, token: str, **parameters):

        self.method = method
        self.endpoint = endpoint
        self.token = token

        self.path = f'https://discord.com/api/v7{endpoint}'

        if parameters:
            self.url = endpoint.format(**{k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        else:
            self.url = self.path

        self.channel_id = parameters.get('channel_id')
        self.guild_id = parameters.get('guild_id')

    @property
    def bucket(self):
        return f'{self.channel_id}:{self.guild_id}:{self.endpoint}'


class MaybeUnlock:

    def __init__(self, lock):
        self.lock = lock
        self.unlock = True

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        if self.unlock:
            self.lock.release()

    def defer(self):
        self.unlock = False


class HTTPClient:

    def __init__(self, bot):
        self.bot = bot
        self.loop = self.bot.loop
        self.session = self.bot.session

        self._locks = weakref.WeakValueDictionary()
        self._global_over = asyncio.Event()
        self._global_over.set()

    async def response_type(self, response):
        data = await response.text(encoding='utf-8')
        if response.headers.get('content-type') == 'application/json':
            return json.loads(data)

        return data

    async def request(self, route: Route, **kwargs):

        lock = self._locks.get(route.bucket)
        if lock is None:
            lock = asyncio.Lock()
            if route.bucket is not None:
                self._locks[route.bucket] = lock

        headers = {
            'X-Ratelimit-Precision': 'millisecond',
            'Authorization': f'Bearer {route.token}'
        }
        kwargs['headers'] = headers

        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:

            for tries in range(5):

                async with self.session.request(route.method, route.url, **kwargs) as response:
                    data = await self.response_type(response)

                    remaining = response.headers.get('X-Ratelimit-Remaining')
                    if remaining == '0' and response.status != 429:

                        reset_after = response.headers.get('X-Ratelimit-Reset-After')
                        if not reset_after:
                            utc = datetime.timezone.utc
                            now = datetime.datetime.now(utc)
                            reset = datetime.datetime.fromtimestamp(float(response.headers['X-Ratelimit-Reset']), utc)
                            delta = (reset - now).total_seconds()
                        else:
                            delta = float(reset_after)

                        maybe_lock.defer()
                        self.loop.call_later(delta, lock.release)

                    if response.status >= 200 or response.status < 300:
                        return data

                    if response.status == 429:
                        if not response.headers.get('Via'):
                            raise exceptions.LifeHTTPError(response, data)

                        retry_after = data['retry_after'] / 1000.0

                        is_global = data.get('global', False)
                        if is_global:
                            self._global_over.clear()

                        await asyncio.sleep(retry_after)

                        if is_global:
                            self._global_over.set()

                        continue

                    if response.status == 500 or response.status == 502:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    if response.status == 403:
                        raise exceptions.LifeHTTPForbidden(response, data)
                    elif response.status == 404:
                        raise exceptions.LifeHTTPNotFound(response, data)
                    else:
                        raise exceptions.LifeHTTPError(response, data)

            raise exceptions.LifeHTTPError(response, data)
