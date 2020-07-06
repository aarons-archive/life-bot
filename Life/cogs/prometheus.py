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

from discord.ext import commands
import prometheus_client


class Prometheus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.dispatch_events = prometheus_client.Counter("dispatch_events", documentation="Dispatch Events",
                                                         namespace="life", labelnames=['event'])

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict):

        event = message.get('t', 'None')
        if event is not None:
            self.bot.dispatch_events.labels(event=event).inc()


def setup(bot):
    bot.add_cog(Prometheus(bot))
