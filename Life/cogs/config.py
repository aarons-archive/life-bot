"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import typing

import discord
from discord.ext import commands

from utilities import checks, context, converters, exceptions, objects


class Config(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

        self.load_task = asyncio.create_task(self.load())

    async def load(self) -> None:

        await self.bot.wait_until_ready()

        guild_configs = await self.bot.db.fetch('SELECT * FROM guild_configs')
        for guild_config in guild_configs:
            if self.bot.guild_configs.get(guild_config['guild_id']) is not None:
                continue
            self.bot.guild_configs[guild_config['guild_id']] = objects.GuildConfig(data=dict(guild_config))

        print(f'[POSTGRESQL] Loaded guild configs. [{len(guild_configs)} guild(s)]')

        user_configs = await self.bot.db.fetch('SELECT * FROM user_configs')
        for user_config in user_configs:
            if self.bot.user_configs.get(user_config['user_id']) is not None:
                continue
            self.bot.user_configs[user_config['user_id']] = objects.UserConfig(data=dict(user_config))

        print(f'[POSTGRESQL] Loaded user configs. [{len(user_configs)} users(s)]')

    async def set_guild_config(self, ctx: context.Context, attribute: str, value: typing.Any, operation: str = 'add') -> None:

        if isinstance(ctx.guild_config, objects.DefaultGuildConfig):
            query = 'INSERT INTO guild_configs (guild_id) values ($1) ON CONFLICT (guild_id) DO UPDATE SET guild_id = excluded.guild_id RETURNING *'
            data = await self.bot.db.fetchrow(query, ctx.guild.id)
            self.bot.guild_configs[ctx.guild.id] = objects.GuildConfig(data=dict(data))

        if attribute == 'prefix':
            query = 'UPDATE guild_configs SET prefixes = array_append(prefixes, $1) WHERE guild_id = $2 RETURNING prefixes'
            if operation == 'remove':
                query = 'UPDATE guild_configs SET prefixes = array_remove(prefixes, $1) WHERE guild_id = $2 RETURNING prefixes'
            if operation == 'clear':
                query = 'UPDATE guild_configs SET prefixes = $1 WHERE guild_id = $2 RETURNING prefixes'
            data = await self.bot.db.fetchrow(query, value, ctx.guild.id)
            ctx.guild_config.prefixes = data['prefixes']

        elif attribute == 'colour':
            query = 'UPDATE guild_configs SET colour = $1 WHERE guild_id = $2 RETURNING *'
            data = await self.bot.db.fetchrow(query, value, ctx.guild.id)
            ctx.guild_config.colour = discord.Colour(int(data['colour'], 16))

    async def set_user_config(self, ctx: context.Context, attribute: str, value: typing.Any, operation: str = 'add') -> None:

        if isinstance(ctx.user_config, objects.DefaultUserConfig):
            query = 'INSERT INTO user_configs (user_id) values ($1) ON CONFLICT (user_id) DO UPDATE SET user_id = excluded.user_id RETURNING *'
            data = await self.bot.db.fetchrow(query, ctx.author.id)
            self.bot.user_configs[ctx.author.id] = objects.UserConfig(data=dict(data))

        elif attribute == 'colour':
            query = 'UPDATE user_configs SET colour = $1 WHERE user_id = $2 RETURNING *'
            data = await self.bot.db.fetchrow(query, value, ctx.author.id)
            ctx.user_config.colour = discord.Colour(int(data['colour'], 16))

    @commands.group(name='config', aliases=['conf'], invoke_without_command=True)
    async def config(self, ctx: context.Context) -> None:
        """
        Display the current server config.
        """

        embed = discord.Embed(colour=ctx.guild_config.colour, title=f'Current configuration:')
        embed.add_field(name='Embed colour:', value=f'`<---` `{str(ctx.guild_config.colour).upper()}`')
        await ctx.send(embed=embed)

    #

    @config.group(name='colour', aliases=['color'], invoke_without_command=True)
    async def config_colour(self, ctx: context.Context) -> None:
        """
        Display the embed colour for this server.
        """

        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'{str(ctx.guild_config.colour).upper()}'))

    @config_colour.command(name='set', aliases=['change'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_colour_set(self, ctx: context.Context, *, colour: commands.ColourConverter) -> None:
        """
        Set the embed colour for this server.

        You must have the `manage server` permission to use this command.

        `colour`: The colour code to use. Must be in the format `0xFFFFFF`, `0x#FFFFFF`, `FFFFFF` or `#FFFFFF`.
        """

        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'Before: {str(ctx.guild_config.colour).upper()}'))
        await self.set_guild_config(ctx=ctx, attribute='colour', value=f'0x{str(colour).strip("#")}')
        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'After: {str(ctx.guild_config.colour).upper()}'))

    @config_colour.command(name='clear', aliases=['revert', 'default', 'delete', 'remove'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_colour_clear(self, ctx: context.Context) -> None:
        """
        Clear the embed colour for this server.

        You must have the `manage server` permission to use this command.
        """

        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'Before: {str(ctx.guild_config.colour).upper()}'))
        await self.set_guild_config(ctx=ctx, attribute='colour', value=f'0x{str(discord.Colour.gold()).strip("#")}')
        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'After: {str(ctx.guild_config.colour).upper()}'))

    #

    @config.group(name='prefix', aliases=['pre'], invoke_without_command=True)
    async def config_prefix(self, ctx: context.Context) -> None:
        """
        Display a list of available prefixes.
        """

        prefixes = await self.bot.get_prefix(ctx.message)

        entries = [f'`1.` {prefixes[1]}']
        entries.extend(f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:]))
        await ctx.paginate_embed(entries=entries, per_page=10, title=f'List of usable prefixes in {ctx.guild if ctx.guild else ctx.channel}.')

    @config_prefix.command(name='add')
    @checks.has_guild_permissions(manage_guild=True)
    async def config_prefix_add(self, ctx: context.Context, prefix: converters.Prefix) -> None:
        """
        Add a prefix to this server.

        You must have the `manage server` permission to use this command.
        Please note that adding a prefix such as `!` and then `!?` will not work as commands will try to match with the first one.

        `prefix`: The prefix to add.
        """

        if len(ctx.guild_config.prefixes) > 20:
            raise exceptions.ArgumentError(f'This server can only have up to 20 prefixes.')
        if prefix in ctx.guild_config.prefixes:
            raise exceptions.ArgumentError(f'This server already has the `{prefix}` prefix.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=prefix)
        await ctx.send(f'Added `{prefix}` to this servers prefixes.')

    @config_prefix.command(name='delete', aliases=['remove'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_prefix_delete(self, ctx: context.Context, prefix: converters.Prefix) -> None:
        """
        Delete a prefix from this server.

        You must have the `manage server` permission to use this command.

        `prefix`: The prefix to delete.
        """

        if not ctx.guild_config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')
        if prefix not in ctx.guild_config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have the `{prefix}` prefix.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=prefix, operation='remove')
        await ctx.send(f'Removed `{prefix}` from this servers prefixes.')

    @config_prefix.command(name='clear', aliases=['revert', 'default'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_prefix_clear(self, ctx: context.Context) -> None:
        """
        Clear all prefixes from this server.

        You must have the `manage server` permission to use this command.
        """

        if not ctx.guild_config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=[], operation='clear')
        await ctx.send(f'Cleared this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
