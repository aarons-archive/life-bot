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
import typing

import spotify

from utilities import context


class Stats:

    __slots__ = ('node', 'stats', 'playing_players', 'players', 'uptime', 'memory_reservable', 'memory_allocated', 'memory_used', 'memory_free', 'system_load',
                 'lavalink_load', 'cpu_cores', 'frames_sent', 'frames_nulled', 'frames_deficit')

    def __init__(self, *, node, stats: dict) -> None:

        self.node = node
        self.stats = stats

        self.playing_players = stats.get('playingPlayers')
        self.players = stats.get('players')
        self.uptime = stats.get('uptime')

        memory = stats.get('memory', {})
        self.memory_reservable = memory.get('reservable', 0)
        self.memory_allocated = memory.get('allocated', 0)
        self.memory_used = memory.get('used', 0)
        self.memory_free = memory.get('free', 0)

        cpu = stats.get('cpu', {})
        self.lavalink_load = cpu.get('lavalinkLoad', 0)
        self.system_load = cpu.get('systemLoad', 0)
        self.cpu_cores = cpu.get('cores', 0)

        frame_stats = stats.get('frameStats', {})
        self.frames_deficit = frame_stats.get('deficit', -1)
        self.frames_nulled = frame_stats.get('nulled', -1)
        self.frames_sent = frame_stats.get('sent', -1)

    def __repr__(self) -> str:
        return f'<LavaLinkNodeStats players={self.players} playing_players={self.playing_players} uptime={self.uptime}>'


class Track:

    __slots__ = ('track_id', 'info', 'ctx', 'identifier', 'is_seekable', 'author', 'length', 'is_stream', 'position', 'title', 'uri', 'requester')

    def __init__(self, *, track_id: str, info: dict, ctx: context.Context = None) -> None:

        self.track_id = track_id
        self.info = info
        self.ctx = ctx

        self.identifier = info.get('identifier')
        self.is_seekable = info.get('isSeekable')
        self.author = info.get('author')
        self.length = info.get('length')
        self.is_stream = info.get('isStream')
        self.position = info.get('position')
        self.title = info.get('title')
        self.uri = info.get('uri')

        if self.ctx is not None:
            self.requester = ctx.author

    def __repr__(self) -> str:
        return f'<LavaLinkTrack title=\'{self.title}\' uri=\'<{self.uri}>\' source=\'{self.source}\' length={self.length}>'

    @property
    def thumbnail(self) -> str:

        thumbnail = None

        if self.source == 'Youtube':
            thumbnail = f'https://img.youtube.com/vi/{self.identifier}/mqdefault.jpg'
        if self.source == 'Spotify':
            thumbnail = self.info.get('thumbnail')

        if thumbnail is None:
            thumbnail = f'https://dummyimage.com/1280x720/000/fff.png&text=+'

        return thumbnail

    @property
    def source(self) -> str:

        if not self.uri:
            return 'Unknown'

        for source in ['youtube', 'vimeo', 'bandcamp', 'soundcloud', 'spotify']:
            if source in self.uri:
                return source.title()

        return 'HTTP'

    @property
    def json(self) -> str:

        data = self.info.copy()
        data['track_id'] = self.track_id
        data['thumbnail'] = self.thumbnail
        data['requester_id'] = self.requester.id
        data['requester_name'] = self.requester.name
        return json.dumps(data)


class Playlist:

    __slots__ = ('playlist_info', 'raw_tracks', 'ctx', 'tracks', 'name', 'selected_track')

    def __init__(self, *, playlist_info: dict, raw_tracks: list, ctx: context.Context = None) -> None:

        self.playlist_info = playlist_info
        self.raw_tracks = raw_tracks
        self.ctx = ctx

        self.tracks = [Track(track_id=track.get('track'), info=track.get('info'), ctx=self.ctx) for track in self.raw_tracks]

        self.name = self.playlist_info.get('name')
        self.selected_track = self.playlist_info.get('selectedTrack')

    def __repr__(self) -> str:
        return f'<LavaLinkPlaylist name=\'{self.name}\' track_count={len(self.tracks)}>'


class Search:

    __slots__ = ('source', 'source_type', 'tracks', 'result')

    def __init__(self, *, source: str, source_type: str, tracks: typing.List[Track],
                 result: typing.Union[spotify.Track, spotify.Album, spotify.Playlist, typing.List[Track], Playlist]):

        self.source = source
        self.source_type = source_type
        self.tracks = tracks
        self.result = result

    def __repr__(self):
        return f'<LavaLinkSearch source=\'{self.source}\' source_type=\'{self.source_type}\' tracks={self.tracks} result={self.tracks}>'


class TrackStartEvent:

    __slots__ = ('data', 'player', 'track')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

        self.track = data.get('track')

    def __str__(self) -> str:
        return 'lavalink_track_start'

    def __repr__(self) -> str:
        return f'<LavaLinkTrackStartEvent player={self.player!r} track={self.track}'


class TrackEndEvent:

    __slots__ = ('data', 'player', 'track', 'reason')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

        self.track = data.get('track')
        self.reason = data.get('reason')

    def __str__(self) -> str:
        return 'lavalink_track_end'

    def __repr__(self) -> str:
        return f'<LavaLinkTrackEndEvent player={self.player!r} track={self.track} reason={self.reason}'


class TrackExceptionEvent:

    __slots__ = ('data', 'player', 'track', 'error')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

        self.track = data.get('track')
        self.error = data.get('error')

    def __str__(self) -> str:
        return 'lavalink_track_exception'

    def __repr__(self) -> str:
        return f'<LavaLinkTrackExceptionEvent player={self.player!r} track={self.track} error={self.error}'


class TrackStuckEvent:

    __slots__ = ('data', 'player', 'track', 'threshold_ms')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

        self.track = data.get('track')
        self.threshold_ms = data.get('thresholdMs')

    def __str__(self) -> str:
        return 'lavalink_track_stuck'

    def __repr__(self) -> str:
        return f'<LavaLinkTrackStuckEvent player={self.player!r} track={self.track} threshold_ms={self.threshold_ms}'


class PlayerConnectedEvent:

    __slots__ = ('data', 'player', 'track', 'threshold_ms')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

    def __str__(self) -> str:
        return 'lavalink_player_connected'

    def __repr__(self) -> str:
        return f'<LavaLinkPlayerConnectedEvent player={self.player!r}'


class PlayerDisconnectedEvent:

    __slots__ = ('data', 'player')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

    def __str__(self) -> str:
        return 'lavalink_player_disconnected'

    def __repr__(self) -> str:
        return f'<LavaLinkPlayerDisconnectedEvent player={self.player!r}'


class WebSocketClosedEvent:

    __slots__ = ('data', 'player', 'track', 'code', 'reason', 'by_remote')

    def __init__(self, *, data: dict) -> None:

        self.data = data
        self.player = data.get('player')

        self.code = data.get('code')
        self.reason = data.get('reason')
        self.by_remote = data.get('byRemote')

    def __str__(self) -> str:
        return 'lavalink_websocket_closed'

    def __repr__(self) -> str:
        return f'<LavaLinkWebSocketClosedEvent player={self.player!r} code={self.code} reason={self.reason} by_remote={self.by_remote}'
