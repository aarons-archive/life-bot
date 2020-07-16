"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import json
from typing import List, Union

import discord
import spotify

from diorite import objects


class LifeTrack(objects.Track):

    __slots__ = ('requester', 'source')

    def __init__(self, track_id: str, info: dict, requester: discord.Member, source: str):
        super().__init__(track_id, info)

        self.requester = requester
        self.source = source

    def __repr__(self):
        return f'<LifeTrack title={self.title!r} uri=<{self.uri}> length={self.length}>'

    @property
    def json(self):

        info = self.info.copy()
        info['thumbnail'] = self.thumbnail

        data = {'track_id': self.track_id, 'info': info, 'source': self.source,
                'requester_id': self.requester.id, 'requester_name': str(self.requester)}

        return json.dumps(data)

    @property
    def thumbnail(self):

        if self.source == 'spotify':
            return self.info.get('thumbnail')

        return f'https://img.youtube.com/vi/{self.identifier}/mqdefault.jpg' if self.yt_id else None


class LifePlaylist(objects.Playlist):

    __slots__ = ('source', 'ctx', 'tracks')

    def __init__(self, playlist_info: dict, tracks: List[objects.Track], requester: discord.Member, source: str):
        super().__init__(playlist_info, tracks)

        self.tracks = [LifeTrack(track_id=track['track'], info=track['info'], requester=requester, source=source)
                       for track in self.raw_tracks]

    def __repr__(self):
        return f'<LifePlaylist name={self.name!r} track_count={len(self.tracks)}>'


class LifeSearch:

    __slots__ = ('source', 'source_type', 'tracks', 'result')

    def __init__(self, source: str, source_type: str, tracks: List[LifeTrack],
                 result: Union[spotify.Track, spotify.Album, spotify.Playlist, List[LifeTrack], LifePlaylist]):

        self.source = source
        self.source_type = source_type
        self.tracks = tracks
        self.result = result

    def __repr__(self):
        return f'<LifeSearch source={self.source!r} source_type={self.source_type!r} result={self.result}>'
