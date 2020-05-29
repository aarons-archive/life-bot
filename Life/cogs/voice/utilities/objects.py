import discord
from discord.ext import commands

from diorite import objects


class LifeTrack(objects.Track):

    def __init__(self, track_id: str, info: dict, ctx: commands.Context):
        super().__init__(track_id, info)

        self.ctx = ctx
        self.requester: discord.Member = ctx.author
        self.channel: discord.TextChannel = ctx.channel


class LifePlaylist(objects.Playlist):

    def __init__(self, playlist_info: dict, tracks: list, ctx: commands.Context):
        super().__init__(playlist_info, tracks)

        self.ctx = ctx
        self.tracks = [LifeTrack(track_id=track['track'], info=track['info'],
                                 ctx=self.ctx) for track in self.raw_tracks]


class SpotifyTrack:

    def __init__(self, ctx: commands.Context, title: str, author: str, length: int, uri: str):

        self.title = title
        self.author = author
        self.length = length
        self.uri = uri

        self.ctx = ctx
        self.requester = ctx.author

    def __repr__(self):
        return f'<LifeSpotifyTrack title={self.title!r} uri=<{self.uri!r}> length={self.length}>'


class Playlist:

    def __init__(self, data: dict):
        self.data = data

        self.id = data.get('id')
        self.name = data.get('name')
        self.owner_id = data.get('owner_id')
        self.private = data.get('private')
        self.creation_date = data.get('creation_date').strftime('%d-%m-%Y: %H:%M')
        self.image_url = data.get('image_url')

        self.tracks = []

    def __repr__(self):
        return f'<LifePlaylist id={self.id!r} name={self.name!r} owner_id={self.owner_id!r}>'

    @property
    def uris(self):
        return [track.uri for track in self.tracks]

    @property
    def is_private(self):
        return 'private' if self.private is True else 'not private'
