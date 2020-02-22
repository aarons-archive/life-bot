from granitepy import objects
from discord.ext import commands


class GraniteTrack(objects.Track):

    def __init__(self, track_id: str, info: dict, ctx: commands.Context):
        super().__init__(track_id, info)

        self.requester = ctx.author


class GranitePlaylist(objects.Playlist):

    def __init__(self, playlist_info: dict, tracks: list, ctx: commands.Context):
        super().__init__(playlist_info, tracks)

        self.tracks = [GraniteTrack(track_id=track["track"], info=track["info"], ctx=ctx) for track in self.tracks_raw]


class Playlist:

    def __init__(self, data: dict):
        self.data = data

        self.id = data.get("id", "N/A")
        self.name = data.get("name", "N/A")
        self.owner_id = data.get("owner_id", "N/A")
        self.private = data.get("private", "N/A")
        self.creation_date = data.get("creation_date", "N/A")
