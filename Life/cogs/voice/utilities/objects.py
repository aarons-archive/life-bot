from typing import List, Union

import discord
import spotify
from diorite import objects
from discord.ext import commands


class SpotifyTrack:

    __slots__ = ('identifier', 'author', 'length', 'title', 'uri', 'thumbnail', 'ctx', 'requester', 'channel')

    def __init__(self, info: dict, ctx: commands.Context):

        self.identifier = info.get('identifier')
        self.author = info.get('author')
        self.length = info.get('length')
        self.title = info.get('title')
        self.uri = info.get('uri')

        self.ctx = ctx
        self.requester = ctx.author
        self.channel = ctx.channel

    def __repr__(self):
        return f'<LifeSpotifyTrack title={self.title!r} author={self.author!r} uri=<{self.uri!r}> length={self.length}>'


class LifeTrack(objects.Track):

    __slots__ = ('ctx', 'requester', 'channel')

    def __init__(self, track_id: str, info: dict, ctx: commands.Context):
        super().__init__(track_id, info)

        self.ctx = ctx
        self.requester: discord.Member = ctx.author
        self.channel: discord.TextChannel = ctx.channel

    def __repr__(self):
        return f'<LifeTrack title={self.title!r} uri=<{self.uri}> length={self.length}>'


class LifePlaylist(objects.Playlist):

    __slots__ = ('ctx', 'tracks')

    def __init__(self, playlist_info: dict, tracks: List[objects.Track], ctx: commands.Context):
        super().__init__(playlist_info, tracks)

        self.ctx = ctx
        self.tracks = [LifeTrack(track_id=track['track'], info=track['info'], ctx=self.ctx)
                       for track in self.raw_tracks]

    def __repr__(self):
        return f'<LifePlaylist name={self.name!r} track_count={len(self.tracks)}>'


class LifeSearch:

    __slots__ = ('source', 'source_type', 'tracks', 'result')

    def __init__(self, source: str, source_type: str, tracks: List[Union[LifeTrack, SpotifyTrack]],
                 result: Union[spotify.Track, spotify.Album, spotify.Playlist, LifeTrack, LifePlaylist]):

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
        return 'private' if self.private is True else 'public'
