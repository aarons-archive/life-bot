"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions


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

    @config.command(name='colour', aliases=['color'])
    async def config_colour(self, ctx: context.Context, operation: str = None, *, value: commands.ColourConverter = None) -> None:
        """
        Manage this server's colour settings.

        Please note that to view the colour, no permissions are needed, however to change it you require the `manage_guild` permission.

        If operation and value are not provided it will display the current colour.

        `operation`: The operation to perform, `set` to set the colour, `reset` to set it back to default and None for displaying the current colour.
        `value`: The colour to set it too. Can be in the format `0x<hex>`, `#<hex>`, `0x#<hex>` or a colour such as red, green, blue.
        """

        if not operation:
            await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=str(ctx.guild_config.colour).upper()))
            return

        if await self.bot.is_owner(person=ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        old_colour = ctx.guild_config.colour

        if operation not in ['set', 'reset']:
            raise exceptions.ArgumentError(f'That was not a valid operation. Use `set` or `reset`.')

        if operation == 'reset':
            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='colour', operation='reset')

        elif operation == 'set':

            if not value:
                raise exceptions.ArgumentError('You did not provide a valid colour argument. They can be `0x<hex>`, `#<hex>`, `0x#<hex>` or a colour such as red or green.')

            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='colour', operation='set', value=f'0x{str(value).strip("#")}')

        await ctx.send(embed=discord.Embed(colour=old_colour, title=f'Old: {str(old_colour).upper()}'))
        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'New: {str(ctx.guild_config.colour).upper()}'))

    @config.command(name='prefix')
    async def config_prefix(self, ctx: context.Context, operation: str = None, value: converters.Prefix = None) -> None:

        if not operation:
            prefixes = await self.bot.get_prefix(ctx.message)
            clean_prefixes = [f'`1.` {prefixes[0]}', *[f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:])]]
            await ctx.paginate_embed(entries=clean_prefixes, per_page=10, colour=ctx.guild_config.colour, title=f'List of usable prefixes.')
            return

        if await self.bot.is_owner(person=ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        if operation not in ['add', 'remove', 'clear']:
            raise exceptions.ArgumentError(f'That was not a valid operation. Use `add`, `remove`, `reset`, `clear`.')

        if operation == 'add':

            if not value:
                raise exceptions.ArgumentError('You did not provide a prefix to add. Valid prefixes are less then 15 characters and contain no backtick (`) characters.')

            if len(ctx.guild_config.prefixes) > 20:
                raise exceptions.ArgumentError(f'This server can only have 20 prefixes.')
            elif value in ctx.guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server already has the prefix `{value}`.')

            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='prefix', operation='add', value=value)
            await ctx.send(f'Added `{value}` to this servers prefixes.')

        elif operation == 'remove':

            if not value:
                raise exceptions.ArgumentError('You did not provide a prefix to remove. Valid prefixes are less then 15 characters and contain no backtick (`) characters.')

            if value not in ctx.guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server does not have the prefix `{value}`.')

            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='prefix', operation='remove', value=value)
            await ctx.send(f'Removed `{value}` from this servers prefixes.')

        elif operation in {'reset', 'clear'}:

            if not ctx.guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server does not have any custom prefixes.')

            await self.bot.guild_manager.edit_guild_config(guild_id=ctx.guild.id, attribute='prefix', operation='reset')
            await ctx.send(f'Cleared this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
