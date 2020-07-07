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

import sys

import discord
import time
import prometheus_client
from discord.ext import commands, tasks


class Prometheus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.socket_events = prometheus_client.Counter('socket_events', documentation='Socket events',
                                                           namespace='life', labelnames=['event'])
        self.bot.counts = prometheus_client.Gauge('counts', documentation='Life counts',
                                                  namespace='life', labelnames=['count'])
        self.bot.stats = prometheus_client.Counter('stats', documentation='Life stats',
                                                   namespace='life', labelnames=['stat'])
        self.bot.info = prometheus_client.Info('misc', documentation='Life info',
                                               namespace='life')

        self.get_stats.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.info.info({'os': sys.platform})
        self.bot.counts.labels(count='members').set(sum([len(guild.members) for guild in self.bot.guilds]))
        self.bot.counts.labels(count='users').set(len(self.bot.users))
        self.bot.counts.labels(count='guilds').set(len(self.bot.guilds))
        self.bot.counts.labels(count='shards').set(len(self.bot.shards))

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict):

        event = message.get('t', 'None')
        if event is not None:
            self.bot.socket_events.labels(event=event).inc()

        if message.get('op') == 11:
            self.bot.counts.labels(count='latency').set(self.bot.latency)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.bot.counts.labels(count='members').inc()
        self.bot.counts.labels(count='users').inc()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.bot.counts.labels(count='members').dec()
        self.bot.counts.labels(count='users').dec()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.bot.counts.labels(count='guilds').inc()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        self.bot.counts.labels(count='guilds').dec()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.bot.stats.labels(stat='messages').inc()

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        self.bot.stats.labels(stat='commands').inc()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        self.bot.stats.labels(stat='commands_errored').inc()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        self.bot.stats.labels(stat='commands_completed').inc()

    @tasks.loop(seconds=20)
    async def get_stats(self):

        with self.bot.process.oneshot():
            memory_info = self.bot.process.memory_full_info()
            physical_memory = memory_info.rss
            virtual_memory = memory_info.vms
            unique_memory = memory_info.uss
            cpu = self.bot.process.cpu_percent(interval=None)

        self.bot.counts.labels(count='threads').set(self.bot.process.num_threads())
        self.bot.counts.labels(count='physical_memory').set(physical_memory)
        self.bot.counts.labels(count='virtual_memory').set(virtual_memory)
        self.bot.counts.labels(count='unique_memory').set(unique_memory)
        self.bot.counts.labels(count='cpu').set(cpu)

        self.bot.counts.labels(count='uptime').set(round(time.time() - self.bot.start_time))


def setup(bot):
    bot.add_cog(Prometheus(bot))
