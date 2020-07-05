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

from typing import List, Union

import discord
import spotify
from discord.ext import commands

from diorite import objects


class SpotifyTrack:

    __slots__ = ('track_id', 'info', 'identifier', 'is_seekable', 'author', 'length', 'is_stream', 'position',
                 'title', 'uri', 'thumbnail', 'source', 'ctx', 'requester', 'channel')

    def __init__(self, info: dict, requester: discord.Member):

        self.track_id = None
        self.info = info

        self.identifier = info.get('identifier')
        self.is_seekable = info.get('isSeekable')
        self.author = info.get('author')
        self.length = info.get('length')
        self.is_stream = info.get('isStream')
        self.title = info.get('title')
        self.position = info.get('position')
        self.uri = info.get('uri')
        self.thumbnail = info.get('thumbnail')

        self.requester = requester
        self.source = 'spotify'

    def __repr__(self):
        return f'<LifeSpotifyTrack title={self.title!r} author={self.author!r} uri=<{self.uri!r}> length={self.length}>'


class LifeTrack(objects.Track):

    __slots__ = ('source', 'ctx', 'requester', 'channel')

    def __init__(self, track_id: str, info: dict, requester: discord.Member):
        super().__init__(track_id, info)

        self.requester = requester
        self.source = 'youtube'

    def __repr__(self):
        return f'<LifeTrack title={self.title!r} uri=<{self.uri}> length={self.length}>'


class LifePlaylist(objects.Playlist):

    __slots__ = ('source', 'ctx', 'tracks')

    def __init__(self, playlist_info: dict, tracks: List[objects.Track], requester: discord.Member):
        super().__init__(playlist_info, tracks)

        self.tracks = [LifeTrack(track_id=track['track'], info=track['info'], requester=requester)
                       for track in self.raw_tracks]

    def __repr__(self):
        return f'<LifePlaylist name={self.name!r} track_count={len(self.tracks)}>'


class LifeSearch:

    __slots__ = ('source', 'source_type', 'tracks', 'result')

    def __init__(self, source: str, source_type: str, tracks: List[Union[LifeTrack, SpotifyTrack]],
                 result: Union[spotify.Track, spotify.Album, spotify.Playlist, List[LifeTrack], LifePlaylist]):

        self.source = source
        self.source_type = source_type
        self.tracks = tracks
        self.result = result

    def __repr__(self):
        return f'<LifeSearch source={self.source!r} source_type={self.source_type!r} result={self.result}>'


class Playlist:

    __slots__ = ('data', 'id', 'name', 'owner_id', 'private', 'creation_date', 'tracks')

    def __init__(self, data: dict):
        self.data = data

        self.id = data.get('id')
        self.name = data.get('name')
        self.owner_id = data.get('owner_id')
        self.private = data.get('private')
        self.creation_date = data.get('creation_date').strftime('%d-%m-%Y: %H:%M')

        self.tracks = []

    def __repr__(self):
        return f'<LifePlaylist id={self.id!r} name={self.name!r} owner_id={self.owner_id!r}>'

    @property
    def is_private(self):
        return 'Private' if self.private is True else 'Public'
