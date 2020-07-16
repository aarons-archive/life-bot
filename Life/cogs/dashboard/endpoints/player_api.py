from abc import ABC
import json

from cogs.dashboard.utilities.endpoint import BaseEndpoint
from tornado.websocket import WebSocketHandler

from cogs.voice.utilities.player import Player


class PlayerInfo(WebSocketHandler, ABC):

    def initialize(self, bot):
        self.bot = bot

    async def on_message(self, message):

        message = json.loads(message)

        guild = self.bot.get_guild(int(message.get('guild_id')))
        if not guild:
            return self.set_status(403)

        member = guild.get_member(int(message.get('user_id')))
        if not member:
            return self.set_status(403)

        player = self.bot.diorite.get_player(guild, cls=Player)

        op = message.get('op')

        if op == 'current':

            data = {'op': 'current', 'data': getattr(player.current, 'json', None)}
            return self.write_message(data)

        elif op == 'position':

            position = {'current': getattr(player.current, 'length', 0), 'position': player.position}
            data = {'op': 'position', 'data': json.dumps(position)}
            return self.write_message(data)


class Skip(BaseEndpoint, ABC):

    async def post(self, guild_id):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to login to use this endpoint.'})

        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return self.set_status(403)

        member = guild.get_member(int(user.id))
        if not member:
            return self.set_status(403)

        player = self.bot.diorite.get_player(guild, cls=Player)

        if not player.is_playing:
            return self.set_status(403)

        channel = getattr(member.voice, 'channel', None)
        if not channel or channel.id != player.voice_channel.id:
            return self.set_status(403)

        if player.current.requester.id != member.id:
            return self.set_status(403)

        await player.stop()
        await self.bot.wait_for('life_track_start', timeout=10.0, check=lambda g_id: g_id == player.guild.id)

        new_track_data = {
            'title': player.current.title,
            'requester': str(player.current.requester),
            'length': player.current.length,
            'author': player.current.author,
            'thumbnail': player.current.thumbnail,
            'uri': player.current.uri
        }
        self.write(new_track_data)


def setup(**kwargs):
    return [(r'/dashboard/(\d+)/skip', Skip, kwargs), (r'/dashboard/(\d+)/player', PlayerInfo, kwargs)]



