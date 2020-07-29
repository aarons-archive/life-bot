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
            self.bot.guild_configs[config['guild_id']] = objects.GuildConfig(data=dict(config))

        print(f'[POSTGRESQL] Loaded guild configs. [{len(configs)} guild(s)]')

    async def load_guild_config(self, guild: discord.Guild, data: dict = None):

        await self.bot.wait_until_ready()

        if not data:
            data = await self.bot.db.fetchrow('SELECT * FROM guild_configs WHERE guild_id = %1', guild.id)

        self.bot.guild_configs[guild.id] = objects.GuildConfig(data=dict(data))

    @commands.group(name='prefix', invoke_without_command=True)
    async def _prefix(self, ctx: context.Context):
        """
        Displays a list of available prefixes.
        """

        prefixes = await self.bot.get_prefix(ctx.message)

        entries = [f'`1.` {prefixes[1]}']
        entries.extend(f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:]))
        return await ctx.paginate_embed(entries=entries, per_page=10, title=f'List of usable prefixes in {ctx.guild}.')

    @_prefix.command(name='add')
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_add(self, ctx: context.Context, prefix: converters.Prefix):
        """
        Adds a prefix to the server.

        Please note that adding a prefix such as `!` and then `!?` will not work as commands will try to match with the first one.

        `prefix`: The prefix to add.
        """

        if isinstance(ctx.config, objects.DefaultGuildConfig) or ctx.config.prefixes is None:
            data = await self.bot.db.fetchrow('INSERT INTO guild_configs (guild_id, prefixes) values ($1, array[$2]) RETURNING *', ctx.guild.id, prefix)
            await self.load_guild_config(guild=ctx.guild, data=data)
            return await ctx.send(f'Added `{prefix}` to this servers prefixes.')

        if prefix in ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server already has the `{prefix}` prefix.')
        if len(ctx.config.prefixes) > 20:
            raise exceptions.ArgumentError(f'This server can only have up to 20 prefixes.')

        data = await self.bot.db.fetchrow('UPDATE guild_configs SET prefixes = array_append(prefixes, $1) WHERE guild_id = $2 RETURNING *', prefix, ctx.guild.id)
        await self.load_guild_config(guild=ctx.guild, data=data)
        return await ctx.send(f'Added `{prefix}` to this servers prefixes.')

    @_prefix.command(name='delete', aliases=['remove'])
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_delete(self, ctx: context.Context, prefix: converters.Prefix):
        """
        Deletes a prefix from the server.

        `prefix`: The prefix to delete.
        """

        if isinstance(ctx.config, objects.DefaultGuildConfig) or not ctx.config.prefixes:
            raise exceptions.ArgumentError('This server does not have any custom prefixes.')
        if prefix not in ctx.config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have the `{prefix}` prefix.')

        data = await self.bot.db.fetchrow('UPDATE guild_configs SET prefixes = array_remove(prefixes, $1) WHERE guild_id = $2 RETURNING *', prefix, ctx.guild.id)
        await self.load_guild_config(guild=ctx.guild, data=data)
        return await ctx.send(f'Removed `{prefix}` from this servers prefixes.')

    @_prefix.command(name='clear')
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_clear(self, ctx: context.Context):
        """
        Clear all prefixes from the server.
        """

        if isinstance(ctx.config, objects.DefaultGuildConfig) or not ctx.config.prefixes:
            raise exceptions.ArgumentError('This server does not have any custom prefixes.')

        data = await self.bot.db.fetchrow('UPDATE guild_configs SET prefixes = $1 WHERE guild_id = $2 RETURNING *', [], ctx.guild.id)
        await self.load_guild_config(guild=ctx.guild, data=data)
        return await ctx.send(f'Cleared this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
