import asyncio
import collections
import random
import typing
import json

from cogs.voice.utilities import objects


class LifeQueue:

    def __init__(self, player):

        self.player = player

        self.getters = collections.deque()
        self.putters = collections.deque()

        self.finished = asyncio.locks.Event(loop=self.player.bot.loop)
        self.finished.set()

        self.unfinished_tasks = 0

        self.queue_list = []

    def __repr__(self):
        return f'<LifeQueue entries={self.size} is_empty={self.is_empty}>'

    def wakeup_next(self, waiters: collections.deque):

        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    def task_done(self):

        if self.unfinished_tasks <= 0:
            raise ValueError('task_done() called too many times')

        self.unfinished_tasks -= 1

        if self.unfinished_tasks == 0:
            self.finished.set()

    @property
    def is_empty(self) -> bool:
        return len(self.queue_list) == 0

    @property
    def size(self) -> int:
        return len(self.queue_list)

    @property
    def json(self):
        return json.dumps([track.json for track in self.queue_list])

    def put(self, item: objects.LifeTrack, position: int = None):

        if position is None:
            self.queue_list.append(item)
        else:
            self.queue_list.insert(position, item)

        self.player.bot.dispatch(f'life_queue_add', self.player.guild.id)

    async def get(self, position: int = 0) -> objects.LifeTrack:

        while self.is_empty:
            getter = self.player.bot.loop.create_future()
            self.getters.append(getter)
            try:
                await getter
            except Exception:
                getter.cancel()
                try:
                    self.getters.remove(getter)
                except ValueError:
                    pass
                if not self.is_empty and not getter.cancelled():
                    self.wakeup_next(self.getters)
                raise
        self.wakeup_next(self.putters)

        return self.queue_list.pop(position)

    def extend(self, items: typing.List[objects.LifeTrack]):

        self.queue_list.extend(items)
        self.player.bot.dispatch(f'life_queue_add', self.player.guild.id)

    def reverse(self):
        self.queue_list.reverse()

    def shuffle(self):
        random.shuffle(self.queue_list)

    def clear(self):
        self.queue_list.clear()
