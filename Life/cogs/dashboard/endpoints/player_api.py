from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint

from cogs.voice.utilities.player import Player


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

        channel = getattr(member.voice, 'channel', None)
        if not channel or channel.id != player.voice_channel.id:
            return self.set_status(403)

        if not player.is_playing:
            return self.set_status(403)

        if player.current.requester.id != member.id:
            return self.set_status(403)

        await player.stop()


def setup(**kwargs):
    return [(r'/dashboard/(\d+)/skip', Skip, kwargs)]



