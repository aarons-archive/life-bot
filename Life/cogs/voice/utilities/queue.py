import asyncio
import collections
import random
import typing


class LifeQueue:

    def __init__(self, player):

        self.player = player

        self.getters = collections.deque()
        self.putters = collections.deque()
        self.unfinished_tasks = 0
        self.finished = asyncio.locks.Event(loop=self.player.bot.loop)
        self.finished.set()

        self.queue_list = []

    def __repr__(self):
        return f'<LifeQueue entries={self.size}>'

    def wakeup_next(self, waiters):

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

        if len(self.queue_list) == 0:
            return True

        return False

    @property
    def size(self) -> int:

        return len(self.queue_list)

    def clear(self) -> None:

        self.queue_list.clear()

    def reverse(self) -> None:

        self.queue_list.reverse()

    def shuffle(self) -> None:

        random.shuffle(self.queue_list)

    def extend(self, items: typing.List[typing.Any]) -> None:

        self.queue_list.extend(items)
        self.player.bot.dispatch(f'life_queue_add', self.player.guild.id)

    def put_pos(self, item: typing.Any, position: int = 0) -> None:
        self.queue_list.insert(position, item)
        self.player.bot.dispatch(f'life_queue_add', self.player.guild)

    def put(self, item: typing.Any) -> None:

        self.queue_list.append(item)
        self.player.bot.dispatch(f'life_queue_add', self.player.guild)

    async def get_pos(self, position: int = 0) -> typing.Any:

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

    async def get(self) -> typing.Any:

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

        return self.queue_list.pop(0)

