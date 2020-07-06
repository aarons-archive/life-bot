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
import discord


class Prometheus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.socket_events = prometheus_client.Counter('socket_events', documentation='Socket events',
                                                           namespace='life', labelnames=['event'])
        self.bot.counts = prometheus_client.Gauge('counts', documentation='Life counts',
                                                  namespace='life', labelnames=['count'])

    @commands.Cog.listener()
    async def on_ready(self):
        print(sum([len(guild.members) for guild in self.bot.guilds]))
        self.bot.counts.labels(count='members').set(sum([len(guild.members) for guild in self.bot.guilds]))
        self.bot.counts.labels(count='users').set(len(self.bot.users))

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict):

        event = message.get('t', 'None')
        if event is not None:
            self.bot.socket_events.labels(event=event).inc()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.bot.counts.labels(count='members').inc()
        self.bot.counts.labels(count='users').inc()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.bot.counts.labels(count='members').dec()
        self.bot.counts.labels(count='users').dec()

def setup(bot):
    bot.add_cog(Prometheus(bot))
