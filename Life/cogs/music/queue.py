import collections
import asyncio


class Queue:

    def __init__(self, bot, maxsize=0):
        self.bot = bot
        self._loop = asyncio.events.get_event_loop()
        self._maxsize = maxsize
        self._getters = collections.deque()
        self._putters = collections.deque()
        self._unfinished_tasks = 0
        self._finished = asyncio.locks.Event(loop=self._loop)
        self._finished.set()
        self.queue = []

    def _format(self):
        result = f'maxsize={self._maxsize!r}'
        if getattr(self, '_queue', None):
            result += f' _queue={list(self.queue)!r}'
        if self._getters:
            result += f' _getters[{len(self._getters)}]'
        if self._putters:
            result += f' _putters[{len(self._putters)}]'
        if self._unfinished_tasks:
            result += f' tasks={self._unfinished_tasks}'
        return result

    @staticmethod
    def _wakeup_next(waiters):
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    @property
    def maxsize(self):
        """
        Return the max queue size.
        """
        return self._maxsize

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received for every
        item that had been put() into the queue).

        Raises ValueError if called more times than there were items placed in
        the queue.
        """
        if self._unfinished_tasks <= 0:
            raise ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        if self._unfinished_tasks == 0:
            self._finished.set()

    def empty(self):
        """
        Return True if the queue is empty, False otherwise.
        """
        if not self.queue:
            return True
        return False

    def full(self):
        """
        Return True if there are maxsize items in the queue.
        """
        if self._maxsize <= 0:
            return False
        return self.size() >= self._maxsize

    def clear(self):
        self.queue.clear()

    def size(self):
        """
        Return number of items in the queue.
        """
        return len(self.queue)

    async def put(self, item):
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.
        """
        while self.full():
            putter = self._loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()
                try:
                    self._putters.remove(putter)
                except ValueError:
                    pass
                if not self.full() and not putter.cancelled():
                    self._wakeup_next(self._putters)
                raise
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)
        self.bot.dispatch("queue_add")
        return self.queue.append(item)

    async def put_pos(self, item, pos):
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.
        """
        while self.full():
            putter = self._loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()
                try:
                    self._putters.remove(putter)
                except ValueError:
                    pass
                if not self.full() and not putter.cancelled():
                    self._wakeup_next(self._putters)
                raise
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)
        self.bot.dispatch("queue_add")
        return self.queue.insert(pos, item)

    async def get(self):
        """Remove and return an item from the queue.

        If queue is empty, wait until an item is available.
        """
        while self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:
                getter.cancel()
                try:
                    self._getters.remove(getter)
                except ValueError:
                    pass
                if not self.empty() and not getter.cancelled():
                    self._wakeup_next(self._getters)
                raise
        item = self.queue.pop(0)
        self._wakeup_next(self._putters)
        return item

    async def get_pos(self, pos):
        """Remove and return an item from the queue.

        If queue is empty, wait until an item is available.
        """
        while self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:
                getter.cancel()
                try:
                    self._getters.remove(getter)
                except ValueError:
                    pass
                if not self.empty() and not getter.cancelled():
                    self._wakeup_next(self._getters)
                raise
        item = self.queue.pop(pos)
        self._wakeup_next(self._putters)
        return item
