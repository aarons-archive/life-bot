import collections
import time

import discord
from discord.ext import commands

from core import colours, config
from core.bot import Life
from utilities import context, converters, exceptions


class Dev(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.group(name='dev', hidden=True, invoke_without_command=True)
    async def dev(self, ctx: context.Context) -> None:
        """
        Base command for bot developer commands.
        """

    @commands.is_owner()
    @dev.command(name='cleanup', aliases=['clean'], hidden=True)
    async def dev_cleanup(self, ctx: context.Context, limit: int = 50) -> None:
        """
        Clean up the bots messages.

        `limit`: The amount of messages to check back through. Defaults to 50.
        """

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            messages = await ctx.channel.purge(check=lambda message: message.author == ctx.me or message.content.startswith(config.PREFIX), bulk=True, limit=limit)
        else:
            messages = await ctx.channel.purge(check=lambda message: message.author == ctx.me, bulk=False, limit=limit)

        s = 's' if len(messages) > 1 else ''
        await ctx.send(f'Found and deleted `{len(messages)}` of my message{s} out of the last `{limit}` message{s}.', delete_after=5)

    @commands.is_owner()
    @dev.command(name='guilds', aliases=['g'], hidden=True)
    async def dev_guilds(self, ctx: context.Context, guilds: int = 20) -> None:
        """
        Display a list of guilds the bot is in.

        `guilds`: The amount of guilds to show per page.
        """

        entries = []

        for guild in sorted(self.bot.guilds, reverse=True, key=lambda _guild: sum(bool(member.bot) for member in _guild.members) / len(_guild.members) * 100):

            total = len(guild.members)
            members = sum(not m.bot for m in guild.members)
            bots = sum(1 for m in guild.members if m.bot)
            percent_bots = f'{round((bots / total) * 100, 2)}%'

            entries.append(f'{guild.id:<19} |{total:<10}|{members:<10}|{bots:<10}|{percent_bots:10}|{guild.name}')

        header = 'Guild id            |Total     |Members   |Bots      |Percent   |Name\n'
        await ctx.paginate(entries=entries, per_page=guilds, header=header, codeblock=True)

    @commands.is_owner()
    @dev.command(name='socketstats', aliases=['ss'], hidden=True)
    async def dev_socket_stats(self, ctx: context.Context) -> None:
        """
        Displays a list of socket event counts since bot startup.
        """

        event_stats = collections.OrderedDict(sorted(self.bot.socket_stats.items(), key=lambda kv: kv[1], reverse=True))
        events_total = sum(event_stats.values())
        events_per_second = round(events_total / round(time.time() - self.bot.start_time))

        description = [f'```py\n{events_total} socket events observed at a rate of {events_per_second} per second.\n']

        for event, count in event_stats.items():
            description.append(f'{event:29} | {count}')

        description.append('```')

        embed = discord.Embed(title=f'{self.bot.user.name} socket stats.', colour=colours.MAIN, description='\n'.join(description))
        await ctx.reply(embed=embed)

    #

    @commands.is_owner()
    @commands.group(name='blacklist', aliases=['bl'], hidden=True, invoke_without_command=True)
    async def blacklist(self, ctx: context.Context) -> None:
        """
        Base command for blacklisting.
        """

        await ctx.reply(f'Choose a valid subcommand. Use `{config.PREFIX}help dev blacklist` for more information.')

    #

    @commands.is_owner()
    @blacklist.group(name='users', aliases=['user', 'u'], hidden=True, invoke_without_command=True)
    async def blacklist_users(self, ctx: context.Context) -> None:
        """
        Display a list of blacklisted users.
        """

        if not (blacklisted := [user_config for user_config in self.bot.user_manager.configs.values() if user_config.blacklisted is True]):
            raise exceptions.ArgumentError('There are no blacklisted users.')

        entries = [f'{user_config.id:<19} | {user_config.blacklisted_reason}' for user_config in blacklisted]
        header = 'User id             | Reason\n'
        await ctx.paginate(entries=entries, per_page=15, header=header, codeblock=True)

    @commands.is_owner()
    @blacklist_users.command(name='add', hidden=True)
    async def blacklist_users_add(self, ctx: context.Context, user: converters.PersonConverter, *, reason: str = 'No reason') -> None:
        """
        Blacklist a user.

        `user`: The user to add to the blacklist.
        `reason`: Reason why the user is being blacklisted.
        """

        if reason == 'No reason':
            reason = f'{user.name} - No reason'

        user_config = self.bot.user_manager.get_config(user.id)
        if user_config.blacklisted is True:
            raise exceptions.ArgumentError('That user is already blacklisted.')

        await user_config.set_blacklisted(True, reason=reason)
        await ctx.reply(f'Added user `{user.id}` to the blacklist with reason:\n\n`{reason}`')

    @commands.is_owner()
    @blacklist_users.command(name='remove', hidden=True)
    async def blacklist_users_remove(self, ctx: context.Context, user: converters.PersonConverter) -> None:
        """
        Unblacklist a user.

        `user`: The user to remove from the blacklist.
        """

        user_config = self.bot.user_manager.get_config(user.id)
        if user_config.blacklisted is False:
            raise exceptions.ArgumentError('That user is not blacklisted.')

        await user_config.set_blacklisted(False)
        await ctx.reply(f'Removed user `{user.id}` from the blacklist.')

    #

    @commands.is_owner()
    @blacklist.group(name='guilds', aliases=['guild', 'g'], hidden=True, invoke_without_command=True)
    async def blacklist_guilds(self, ctx: context.Context) -> None:
        """
        Display a list of blacklisted guilds.
        """

        if not (blacklisted := [guild_config for guild_config in self.bot.guild_manager.configs.values() if guild_config.blacklisted is True]):
            raise exceptions.ArgumentError('There are no blacklisted guilds.')

        entries = [f'{guild_config.id:<19} | {guild_config.blacklisted_reason}' for guild_config in blacklisted]
        header = 'Guild id            | Reason\n'
        await ctx.paginate(entries=entries, per_page=10, header=header, codeblock=True)

    @commands.is_owner()
    @blacklist_guilds.command(name='add', hidden=True)
    async def blacklist_guilds_add(self, ctx: context.Context, guild_id: int, *, reason: str = 'No reason') -> None:
        """
        Blacklist a guild.

        `guild`: The guild id to add to the blacklist.
        `reason`: Reason why the guild is being blacklisted.
        """

        if 17 > guild_id > 20:
            raise exceptions.ArgumentError('That is not a valid guild id.')

        if (guild := self.bot.get_guild(guild_id)) and reason == 'No reason':
            reason = f'{guild.name} - No reason'
            await guild.leave()

        guild_config = self.bot.guild_manager.get_config(guild_id)
        if guild_config.blacklisted is True:
            raise exceptions.ArgumentError('The guild is already blacklisted.')

        await guild_config.set_blacklisted(True, reason=reason)
        await ctx.reply(f'Blacklisted guild `{guild_id}` with reason:\n\n`{reason}`')

    @commands.is_owner()
    @blacklist_guilds.command(name='remove', hidden=True)
    async def blacklist_guilds_remove(self, ctx: context.Context, guild_id: int) -> None:
        """
        Unblacklist a guild.

        `guild`: The guild id to remove from the blacklist.
        """

        if 17 > guild_id > 20:
            raise exceptions.ArgumentError('That is not a valid guild id.')

        guild_config = self.bot.guild_manager.get_config(guild_id)
        if guild_config.blacklisted is False:
            raise exceptions.ArgumentError('That guild is not blacklisted.')

        await guild_config.set_blacklisted(False)
        await ctx.reply(f'Unblacklisted guild `{guild_id}`.')


def setup(bot: Life) -> None:
    bot.add_cog(Dev(bot=bot))
