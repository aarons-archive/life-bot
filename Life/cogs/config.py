"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands

from bot import Life
from utilities import checks, context, converters, exceptions


class Config(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name='config', invoke_without_command=True)
    async def config(self, ctx: context.Context) -> None:
        """
        Display the servers config.
        """

        prefixes = ', '.join([f'`{prefix}`' for prefix in ctx.guild_config.prefixes])

        embed = discord.Embed(colour=ctx.guild_config.colour, title=f'Guild config:', description=f'`Prefixes:` {prefixes}')
        embed.add_field(name='Embed colour:', value=f'`<---` `{str(ctx.guild_config.colour).upper()}`')
        await ctx.send(embed=embed)

    @config.group(name='colour', aliases=['color'], invoke_without_command=True)
    async def config_colour(self, ctx: context.Context, operation: str = None, value: commands.ColourConverter = None) -> None:
        """
        Display the embed colour for this server.
        """

        if not operation:
            await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=str(ctx.guild_config.colour).upper()))
            return

        old_colour = ctx.guild_config.colour

        if operation == 'reset' and value is None:
            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='colour', operation='reset')
        elif operation == 'set' and value is not None:
            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='colour', operation='set', value=f'0x{str(value).strip("#")}')
        else:
            raise exceptions.ArgumentError(f'That was not a valid operation. Use `set` or `reset`.')

        await ctx.send(embed=discord.Embed(colour=old_colour, title=f'Old: {str(old_colour).upper()}'))
        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'New: {str(ctx.guild_config.colour).upper()}'))




    @config.group(name='prefix', invoke_without_command=True)
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

        await self.bot.set_guild_config(guild=ctx.guild, attribute='prefix', value=prefix)
        await ctx.send(f'Added `{prefix}` to this servers prefixes.')

    @config_prefix.command(name='remove')
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

        await self.bot.set_guild_config(guild=ctx.guild, attribute='prefix', value=prefix, operation='remove')
        await ctx.send(f'Removed `{prefix}` from this servers prefixes.')

    @config_prefix.command(name='clear', aliases=['default'])
    @checks.has_guild_permissions(manage_guild=True)
    async def config_prefix_clear(self, ctx: context.Context) -> None:
        """
        Clear all prefixes from this server.

        You must have the `manage server` permission to use this command.
        """

        if not ctx.guild_config.prefixes:
            raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')

        await self.bot.set_guild_config(guild=ctx.guild, attribute='prefix', value=[], operation='clear')
        await ctx.send(f'Cleared this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
