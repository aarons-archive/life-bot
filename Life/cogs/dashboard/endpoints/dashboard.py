#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from abc import ABC

from cogs.dashboard.utilities.bases import BaseHTTPHandler


# noinspection PyAsyncCall
class Dashboard(BaseHTTPHandler, ABC):

    async def get(self, guild_id):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to login to view this page.'})

        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            self.set_status(400)
            return await self.finish({'error': 'i am not in that guild.'})

        member = guild.get_member(int(user.id))
        if not member:
            self.set_status(403)
            return await self.finish({'error': 'you are not in that guild.'})

        self.render('dashboard.html', bot=self.bot, user=user, guild=guild, player=guild.voice_client)


def setup(**kwargs):
    return [(r'/dashboard/(\d+)', Dashboard, kwargs)]
