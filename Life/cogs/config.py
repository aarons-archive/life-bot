"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import typing
import discord

from discord.ext import commands

from cogs.utilities import checks, converters, exceptions, objects
from utilities import context


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.load_task = asyncio.create_task(self.load())

    async def load(self):

        await self.bot.wait_until_ready()

        configs = await self.bot.db.fetch('SELECT * FROM guild_configs')
        for config in configs:
            if self.bot.guild_configs.get(config['guild_id']) is not None:
                continue
            self.bot.guild_configs[config['guild_id']] = objects.GuildConfig(data=dict(config))

        print(f'[POSTGRESQL] Loaded guild configs. [{len(configs)} guild(s)]')

    async def set_guild_config(self, ctx: context.Context, attribute: str, value: typing.Any, operation: str = 'add'):

        if isinstance(ctx.config, objects.DefaultGuildConfig):
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
            ctx.config.prefixes = data['prefixes']

        elif attribute == 'colour':
            query = 'UPDATE guild_configs SET colour = $1 WHERE guild_id = $2 RETURNING *'
            data = await self.bot.db.fetchrow(query, value, ctx.guild.id)
            ctx.config.colour = discord.Colour(int(data['colour'], 16))

    @commands.group(name='config', aliases=['configuration'], invoke_without_command=True)
    async def config(self, ctx: context.Context):
        """
        Display the current server/channel config.
        """

        embed = discord.Embed(colour=ctx.config.colour, title=f'Current configuration:')
        embed.add_field(name='Embed colour:', value=f'`<---` `{str(ctx.config.colour).upper()}`')
        return await ctx.send(embed=embed)

    #

    @config.group(name='colour', aliases=['color'], invoke_without_command=True)
    async def config_colour(self, ctx: context.Context):
        """
        Display the current server/channel embed colour.
        """

        embed = discord.Embed(colour=ctx.config.colour, title=f'{str(ctx.config.colour).upper()}')
        return await ctx.send(embed=embed)

    @config_colour.command(name='set', aliases=['change'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_colour_set(self, ctx: context.Context, hexcode: str):
        """
        Set the embed colour for this server.

        You must have the `manage server` permission to use this command.

        `hexcode`: The colour code to set embeds too. Must be in the format `#FFFFFF`
        """

        if self.bot.hex_colour_regex.match(hexcode) is None:
            raise exceptions.ArgumentError(f'The colour code `{hexcode}` is invalid. Please use the format `#FFFFFF`.')

        await ctx.send(embed=discord.Embed(colour=ctx.config.colour, title='Before'))
        await self.set_guild_config(ctx=ctx, attribute='colour', value=f'0x{hexcode.strip("#")}')
        return await ctx.send(embed=discord.Embed(colour=ctx.config.colour, title='After'))

    @config_colour.command(name='clear', aliases=['revert', 'default'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_colour_clear(self, ctx: context.Context):
        """
        Set the embed colour for this server back to default.

        You must have the `manage server` permission to use this command.
        """

        await ctx.send(embed=discord.Embed(colour=ctx.config.colour, title='Before'))
        await self.set_guild_config(ctx=ctx, attribute='colour', value=f'0x{str(discord.Colour.gold()).strip("#")}')
        return await ctx.send(embed=discord.Embed(colour=ctx.config.colour, title='After'))

    #

    @commands.group(name='prefix', invoke_without_command=True)
    async def _prefix(self, ctx: context.Context):
        """
        Display a list of available prefixes.
        """

        prefixes = await self.bot.get_prefix(ctx.message)

        entries = [f'`1.` {prefixes[1]}']
        entries.extend(f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:]))
        return await ctx.paginate_embed(entries=entries, per_page=10, title=f'List of usable prefixes in {ctx.guild if ctx.guild else ctx.channel}.')

    @_prefix.command(name='add')
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_add(self, ctx: context.Context, prefix: converters.Prefix):
        """
        Add a prefix to this server.

        You must have the `manage server` permission to use this command.

        Please note that adding a prefix such as `!` and then `!?` will not work as commands will try to match with the first one.

        `prefix`: The prefix to add.
        """

        if len(ctx.config.prefixes) > 20:
            raise exceptions.ArgumentError(f'This server can only have up to 20 prefixes.')
        if prefix in ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server already has the `{prefix}` prefix.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=prefix)
        return await ctx.send(f'Added `{prefix}` to this server\'s prefixes.')

    @_prefix.command(name='delete', aliases=['remove'])
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_delete(self, ctx: context.Context, prefix: converters.Prefix):
        """
        Delete a prefix from this server.

        You must have the `manage server` permission to use this command.

        `prefix`: The prefix to delete.
        """

        if not ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')
        if prefix not in ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have the `{prefix}` prefix.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=prefix, operation='remove')
        return await ctx.send(f'Removed `{prefix}` from this server\'s prefixes.')

    @_prefix.command(name='clear', aliases=['revert', 'default'])
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_clear(self, ctx: context.Context):
        """
        Clear all prefixes from this server.

        You must have the `manage server` permission to use this command.
        """

        if not ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')

        await self.set_guild_config(ctx=ctx, attribute='prefix', value=[], operation='clear')
        return await ctx.send(f'Cleared this server\'s prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
