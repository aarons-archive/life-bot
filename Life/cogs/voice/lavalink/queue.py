import asyncio
import collections
import random
import typing

from cogs.voice.lavalink import objects


class Queue:

    def __init__(self, *, player) -> None:

        self.player = player

        self.queue = []
        self.queue_history = []
        self.looping = False

        self._getters = collections.deque()
        self._putters = collections.deque()

        self._finished = asyncio.Event()
        self._finished.set()
        self._unfinished_tasks = 0

    def __repr__(self) -> str:
        return f'<LavaLinkQueue length={len(self)}>'

    def __iter__(self) -> typing.Iterator:
        return self.queue.__iter__()

    def __contains__(self, item: objects.Track) -> bool:
        return True if item in self.queue else False

    def __getitem__(self, key: slice) -> list:
        return self.queue[key]

    def __len__(self) -> int:
        return len(self.queue)

    def _task_done(self) -> None:

        if self._unfinished_tasks <= 0:
            raise ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        if self._unfinished_tasks == 0:
            self._finished.set()

    def _wakeup_next(self, waiters: collections.deque) -> None:

        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    @property
    def is_empty(self) -> bool:
        return True if not self.queue else False

    @property
    def is_looping(self) -> bool:
        return True if self.looping is True else False

    async def get(self, *, position: int = 0) -> objects.Track:

        while self.is_empty:
            _getter = self.player.bot.loop.create_future()
            self._getters.append(_getter)
            try:
                await _getter
            except Exception:
                _getter.cancel()
                try:
                    self._getters.remove(_getter)
                except ValueError:
                    pass
                if not self.is_empty and not _getter.cancelled():
                    self._wakeup_next(self._getters)
                raise
        self._wakeup_next(self._putters)

        item = self.queue.pop(position)
        self.queue_history.append(item)
        return item

    def put(self, *, item: objects.Track, position: int = None) -> objects.Track:

        if position is None:
            self.queue.append(item)
            self.player.wait_queue_add.set()
            return item

        self.queue.insert(position, item)
        self.player.wait_queue_add.set()
        return item

    def extend(self, *, items: typing.List[objects.Track]) -> typing.List[objects.Track]:

        self.queue.extend(items)
        self.player.wait_queue_add.set()
        return items

    def shuffle(self) -> None:
        random.shuffle(self.queue)

    def reverse(self) -> None:
        self.queue.reverse()

    def clear(self) -> None:
        self.queue.clear()


    def get_previous(self) -> typing.Optional:

        if not self.queue_history:
            return None

        return self.queue_history[-1]

    def history(self) -> typing.Generator:

        for item in reversed(self.queue_history):
            yield item

    def clear_history(self) -> None:
        self.queue_history.clear()
