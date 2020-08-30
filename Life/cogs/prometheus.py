"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import time

import discord
import prometheus_client
import psutil
from discord.ext import commands, tasks

from bot import Life


# noinspection PyUnusedLocal
class Prometheus(commands.Cog):

    def __init__(self, bot: Life):
        self.bot = bot

        self.process = psutil.Process()
        
        self.socket_events = prometheus_client.Counter('socket_events', documentation='Socket events', namespace='life', labelnames=['event'])
        self.counters = prometheus_client.Counter('stats', documentation='Life stats', namespace='life', labelnames=['stat'])
        self.gauges = prometheus_client.Gauge('counts', documentation='Life counts', namespace='life', labelnames=['count'])
        self.info = prometheus_client.Info('misc', documentation='Life info', namespace='life')

        self.collect_stats.start()

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.info.info({'os': sys.platform})
        self.gauges.labels(count='members').set(sum([len(guild.members) for guild in self.bot.guilds]))
        self.gauges.labels(count='users').set(len(self.bot.users))
        self.gauges.labels(count='guilds').set(len(self.bot.guilds))

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict) -> None:

        event = message.get('t', 'None')
        if event is not None:
            self.socket_events.labels(event=event).inc()

        if message.get('op') == 11:
            self.gauges.labels(count='latency').set(self.bot.latency)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:

        self.gauges.labels(count='members').inc()
        self.gauges.labels(count='users').set(len(self.bot.users))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:

        self.gauges.labels(count='members').dec()
        self.gauges.labels(count='users').set(len(self.bot.users))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.gauges.labels(count='guilds').inc()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.gauges.labels(count='guilds').dec()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        self.counters.labels(stat='messages').inc()

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        self.counters.labels(stat='commands').inc()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context) -> None:
        self.counters.labels(stat='commands_completed').inc()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:

        error = getattr(error, 'original', error)
        if isinstance(error, (commands.CommandNotFound, commands.CommandOnCooldown, commands.MaxConcurrencyReached, commands.CheckFailure)):
            return

        self.counters.labels(stat='commands_errored').inc()

    @tasks.loop(seconds=60)
    async def collect_stats(self) -> None:

        await self.bot.wait_until_ready()

        with self.process.oneshot():
            self.gauges.labels(count='cpu').set(self.process.cpu_percent(interval=None))
            self.gauges.labels(count='threads').set(self.process.num_threads())

            memory_info = self.process.memory_full_info()
            self.gauges.labels(count='physical_memory').set(memory_info.rss)
            self.gauges.labels(count='virtual_memory').set(memory_info.vms)
            self.gauges.labels(count='unique_memory').set(memory_info.uss)

        self.gauges.labels(count='uptime').set(round(time.time() - self.bot.start_time))

        payload = {
            'metrics': {event: count for event, count in self.bot.socket_stats.items()},
            'usercount': len(self.bot.users),
            'guildcount': len(self.bot.guilds),
            'latency': round(self.bot.latency * 1000),
            'ramusage': round(memory_info.rss / 1048576),
        }
        async with self.bot.session.post('https://idevision.net/api/bots/updates', json=payload, headers={"Authorization": self.bot.config.idevision_key}) as post:
            if post.status != 200:
                pass


def setup(bot):
    bot.add_cog(Prometheus(bot))
