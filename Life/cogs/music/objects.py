from granitepy import objects
from discord.ext import commands


class Track(objects.Track):

    def __init__(self, track_id: str, info: dict, ctx: commands.Context):
        super().__init__(track_id, info)

        self.requester = ctx.author


class Playlist(objects.Playlist):

    def __init__(self, playlist_info: dict, tracks: list, ctx: commands.Context):
        super().__init__(playlist_info, tracks)

        self.tracks = [Track(track_id=track["track"], info=track["info"], ctx=ctx) for track in self.tracks_raw]
