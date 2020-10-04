"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import collections
import sys
import time

import discord
import humanize
import pkg_resources
import setproctitle
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions


class Dev(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.group(name='dev', hidden=True, invoke_without_command=True)
    async def dev(self, ctx: context.Context) -> None:
        """
        Base command for bot developer commands.

        Displays a message with stats about the bot.
        """

        python_version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        discordpy_version = pkg_resources.get_distribution('discord.py').version
        platform = sys.platform
        process_name = setproctitle.getproctitle()
        process_id = self.bot.process.pid
        thread_count = self.bot.process.num_threads()

        description = [f'I am running on the python version **{python_version}** on the OS **{platform}** using the discord.py version **{discordpy_version}**. '
                       f'The process is running as **{process_name}** on PID **{process_id}** and is using **{thread_count}** threads.']

        if isinstance(self.bot, commands.AutoShardedBot):
            description.append(f'The bot is automatically sharded with **{self.bot.shard_count}** shard(s) and can see **{len(self.bot.guilds)}** guilds and '
                               f'**{len(self.bot.users)}** users.')
        else:
            description.append(f'The bot is not sharded and can see **{len(self.bot.guilds)}** guilds and **{len(self.bot.users)}** users.')

        with self.bot.process.oneshot():

            memory_info = self.bot.process.memory_full_info()
            physical_memory = humanize.naturalsize(memory_info.rss)
            virtual_memory = humanize.naturalsize(memory_info.vms)
            unique_memory = humanize.naturalsize(memory_info.uss)
            cpu_usage = self.bot.process.cpu_percent(interval=None)

            description.append(f'The process is using **{physical_memory}** of physical memory, **{virtual_memory}** of virtual memory and **{unique_memory}** of memory '
                               f'that is unique to the process. It is also using **{cpu_usage}%** of CPU.')

        embed = discord.Embed(title=f'{self.bot.user.name} bot information page.', colour=0xF5F5F5)
        embed.description = '\n\n'.join(description)

        await ctx.send(embed=embed)

    @commands.is_owner()
    @dev.command(name='cleanup', aliases=['clean'], hidden=True)
    async def dev_cleanup(self, ctx: context.Context, limit: int = 50) -> None:
        """
        Cleans up the bots messages.

        `limit`: The amount of messages to check back through. Defaults to 50.
        """

        prefix = self.bot.config.prefix

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            messages = await ctx.channel.purge(check=lambda message: message.author == ctx.me or message.content.startswith(prefix), bulk=True, limit=limit)
        else:
            messages = await ctx.channel.purge(check=lambda message: message.author == ctx.me, bulk=False, limit=limit)

        await ctx.send(f'Found and deleted `{len(messages)}` of my message(s) out of the last `{limit}` message(s).', delete_after=3)

    @commands.is_owner()
    @dev.command(name='guilds', aliases=['guildlist', 'gl'], hidden=True)
    async def dev_guilds(self, ctx: context.Context, guilds: int = 20) -> None:
        """
        Displays a list of guilds the bot is in.

        `guilds`: The amount of guilds to show per page.
        """

        entries = []

        for guild in sorted(self.bot.guilds, reverse=True, key=lambda _guild: (sum(1 for member in _guild.members if member.bot) / len(_guild.members)) * 100):

            total = len(guild.members)
            members = sum(1 for m in guild.members if not m.bot)
            bots = sum(1 for m in guild.members if m.bot)
            percent_bots = f'{round((bots / total) * 100, 2)}%'

            entries.append(f'{guild.id:<19} |{total:<10}|{members:<10}|{bots:<10}|{percent_bots:10}|{guild.name}')

        header = 'Guild id            |Total     |Members   |Bots      |Percent   |Name\n'
        await ctx.paginate(entries=entries, per_page=guilds, header=header, codeblock=True)

    @commands.is_owner()
    @dev.command(name='socketstats', aliases=['ss'], hidden=True)
    async def dev_socket_stats(self, ctx: context.Context) -> None:
        """
        Displays a list of socket event counts since startup.
        """

        event_stats = collections.OrderedDict(sorted(self.bot.socket_stats.items(), key=lambda kv: kv[1], reverse=True))
        events_total = sum(event_stats.values())
        events_per_second = round(events_total / round(time.time() - self.bot.start_time))

        description = [f'```py\n{events_total} socket events observed at a rate of {events_per_second} per second.\n']

        for event, count in event_stats.items():
            description.append(f'{event:29} | {count}')

        description.append('```')

        embed = discord.Embed(title=f'{self.bot.user.name} socket stats.', colour=ctx.colour, description='\n'.join(description))
        await ctx.send(embed=embed)

    @dev.group(name='blacklist', aliases=['bl'], hidden=True, invoke_without_command=True)
    async def dev_blacklist(self, ctx: context.Context) -> None:
        """
        Base command for blacklisting.
        """

        await ctx.send(f'Choose a valid subcommand. Use `{self.bot.config.prefix}help dev blacklist` for more information.')

    @dev_blacklist.group(name='user', hidden=True, invoke_without_command=True)
    async def dev_blacklist_user(self, ctx: context.Context) -> None:
        """
        Display a list of blacklisted users.
        """

        blacklist = {user_id: user_config for user_id, user_config in self.bot.user_manager.configs.items() if user_config.blacklisted is True}
        blacklisted = []

        if not blacklist:
            raise exceptions.ArgumentError('There are no blacklisted users.')

        for user_id, user_config in blacklist.items():
            try:
                user = await self.bot.fetch_user(user_id)
                blacklisted.append(f'{user.id:<19} |{user.name:<32} |{user_config.blacklisted_reason}')
            except discord.NotFound:
                blacklisted.append(f'{user_id:<19} |{"Not found":<32} |{user_config.blacklisted_reason}')

        header = 'User id             |Name                             |Reason\n'
        await ctx.paginate(entries=blacklisted, per_page=10, header=header, codeblock=True)

    @dev_blacklist_user.command(name='add', hidden=True)
    async def dev_blacklist_user_add(self, ctx: context.Context, user: converters.User, *, reason: str = None) -> None:
        """
        Blacklist a user.

        `user`: The user to add to the blacklist.
        `reason`: Reason why the user is being blacklisted.
        """

        if not reason:
            reason = user.name

        user_config = self.bot.user_manager.get_user_config(user_id=user.id)
        if user_config.blacklisted is True:
            raise exceptions.ArgumentError(f'`{user} - {user.id}` is already blacklisted.')

        await self.bot.user_manager.edit_user_config(user_id=user.id, attribute='blacklist', operation='set', value=reason)
        await ctx.send(f'`{user} - {user.id}` is now blacklisted with reason:\n\n`{reason}`')

    @dev_blacklist_user.command(name='remove', hidden=True)
    async def dev_blacklist_user_remove(self, ctx: context.Context, user: converters.User) -> None:
        """
        Unblacklist a user.

        `user`: The user to remove from the blacklist.
        """

        user_config = self.bot.user_manager.get_user_config(user_id=user.id)
        if user_config.blacklisted is False:
            raise exceptions.ArgumentError(f'`{user} - {user.id}` is not blacklisted.')

        await self.bot.user_manager.edit_user_config(user_id=user.id, attribute='blacklist', operation='reset')
        await ctx.send(f'`{user} - {user.id}` is now unblacklisted.')

    @dev_blacklist.group(name='guild', hidden=True, invoke_without_command=True)
    async def dev_blacklist_guild(self, ctx: context.Context) -> None:
        """
        Display a list of blacklisted guilds.
        """

        blacklist = {guild_id: guild_config for guild_id, guild_config in self.bot.guild_manager.configs.items() if guild_config.blacklisted is True}
        blacklisted = []

        if not blacklist:
            raise exceptions.ArgumentError('There are no blacklisted guilds.')

        for guild_id, guild_config in blacklist.items():
            guild = self.bot.get_guild(guild_id)
            if guild is not None:
                blacklisted.append(f'{guild.id:<19} |{guild.name:<32} |{guild_config.blacklisted_reason}')
            else:
                blacklisted.append(f'{guild_id:<19} |{"Not found":<32} |{guild_config.blacklisted_reason}')

        header = 'Guild id            |Name                             |Reason\n'
        await ctx.paginate(entries=blacklisted, per_page=10, header=header, codeblock=True)

    @dev_blacklist_guild.command(name='add', hidden=True)
    async def dev_blacklist_guild_add(self, ctx: context.Context, guild_id: int, *, reason: str = None) -> None:
        """
        Add a guild to the blacklist.

        `guild`: The guild to add to the blacklist.
        `reason`: Reason why the guild is being blacklisted.
        """

        if 17 > guild_id > 20:
            raise exceptions.ArgumentError('That is not a valid guild id.')

        guild = self.bot.get_guild(guild_id)

        if guild:
            guild_name = guild.name
            if not reason:
                reason = f'{guild.name}'
        else:
            guild_name = 'Not found'
            if not reason:
                reason = 'No reason'

        guild_config = self.bot.guild_manager.get_guild_config(guild_id=guild_id)
        if guild_config.blacklisted is True:
            raise exceptions.ArgumentError(f'The guild `{guild_name} - {guild_id}` is already blacklisted.')

        await self.bot.guild_manager.edit_guild_config(guild_id=guild_id, attribute='blacklist', operation='set', value=reason)
        await ctx.send(f'The guild `{guild_name} - {guild_id}` is now blacklisted with reason:\n\n`{reason}`')

    @dev_blacklist_guild.command(name='remove', hidden=True)
    async def dev_blacklist_guild_remove(self, ctx: context.Context, guild_id: int) -> None:
        """
        Unblacklist a guild.

        `guild`: The guild to remove from the blacklist.
        """

        if 17 > guild_id > 20:
            raise exceptions.ArgumentError('That is not a valid guild id.')

        guild = self.bot.get_guild(guild_id)
        if guild:
            guild_name = guild.name
        else:
            guild_name = 'Not found'

        guild_config = self.bot.guild_manager.get_guild_config(guild_id=guild_id)
        if guild_config.blacklisted is False:
            raise exceptions.ArgumentError(f'The guild `{guild_name} - {guild_id}` is not blacklisted.')

        await self.bot.guild_manager.edit_guild_config(guild_id=guild_id, attribute='blacklist', operation='reset')
        await ctx.send(f'The guild `{guild_name} - {guild_id}` is now unblacklisted.')


def setup(bot):
    bot.add_cog(Dev(bot))
