"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""
import json
import random
import typing

from cogs.voice.lavalink import objects


class Queue:

    def __init__(self, *, player) -> None:

        self.player = player

        self.queue = []
        self.queue_history = []
        self.looping = False

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

    @property
    def is_empty(self) -> bool:
        return True if not self.queue else False

    @property
    def is_looping(self) -> bool:
        return True if self.looping is True else False

    @property
    def json(self) -> str:

        data = {
            'queue': [item.json for item in self.queue],
            'queue_history': [item.json for item in self.queue_history],
            'is_looping': self.is_looping,
        }
        return json.dumps(data)

    @property
    def history(self) -> typing.Generator:

        for item in self.queue_history[1:]:
            yield item

    async def get(self, *, position: int = 0, history: bool = True) -> typing.Optional[objects.Track]:

        try:
            item = self.queue.pop(position)
        except IndexError:
            return None

        if history is True:
            self.put_history(tracks=item, position=position)

        return item

    def get_history(self, *, position: int = 0) -> typing.Optional[objects.Track]:

        history = list(reversed(self.queue_history))

        try:
            item = history[position]
        except IndexError:
            return None

        return item

    def put(self, *, tracks: typing.Union[objects.Track, typing.List[objects.Track]], position: int = None) -> None:

        if position is None:
            if isinstance(tracks, objects.Track):
                self.queue.append(tracks)
            else:
                self.queue.extend(tracks)
        else:
            if isinstance(tracks, objects.Track):
                self.queue.insert(position, tracks)
            else:
                for index, track, in enumerate(tracks):
                    self.queue.insert(position + index, track)

        self.player.wait_queue_add.set()
        self.player.wait_queue_add.clear()

    def put_history(self, *, tracks: typing.Union[objects.Track, typing.List[objects.Track]], position: int = None) -> None:

        if position is None:
            if isinstance(tracks, objects.Track):
                self.queue_history.append(tracks)
            else:
                self.queue_history.extend(tracks)
        else:
            if isinstance(tracks, objects.Track):
                self.queue_history.insert(position, tracks)
            else:
                for index, track, in enumerate(tracks):
                    self.queue_history.insert(position + index, track)

    def sort(self, method: str = 'title', reverse: bool = False) -> None:

        if method == 'title':
            self.queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == 'author':
            self.queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == 'length':
            self.queue.sort(key=lambda track: track.length, reverse=reverse)

    def shuffle(self) -> None:
        random.shuffle(self.queue)

    def reverse(self) -> None:
        self.queue.reverse()

    def clear(self) -> None:
        self.queue.clear()

    def clear_history(self) -> None:
        self.queue_history.clear()
