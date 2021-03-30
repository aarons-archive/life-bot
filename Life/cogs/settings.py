#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from typing import Literal

import discord
from discord.ext import commands

import config
from bot import Life
from utilities import context, converters, enums, exceptions


class Settings(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name='settings', aliases=['config'], invoke_without_command=True)
    async def settings(self, ctx: context.Context) -> None:
        """
        Display this servers settings.
        """

        prefixes = ', '.join(f'`{prefix}`' for prefix in ctx.guild_config.prefixes)

        embed = discord.Embed(
                colour=ctx.guild_config.colour,
                title='Guild settings:',
                description=f'`Prefixes:` {prefixes}\n'
                            f'`Embed size:` {ctx.guild_config.embed_size.name.upper()}'
        )
        embed.add_field(name='Embed colour:', value=f'`<---` `{str(ctx.guild_config.colour).upper()}`')
        await ctx.send(embed=embed)

    @settings.command(name='colour', aliases=['color'])
    async def settings_colour(self, ctx: context.Context, operation: Literal['set', 'reset'] = None, *, colour: commands.ColourConverter = None) -> None:
        """
        Manage this servers colour settings.

        Please note that to view the colour, no permissions are needed, however to change it you require the `manage_guild` permission.

        `operation`: The operation to perform, `set` to set the colour, `reset` to revert back to the default. If not provided the current colour will be displayed.
        `colour`: The colour to set. Possible formats include `0x<hex>`, `#<hex>`, `0x#<hex>` and `rgb(<number>, <number>, <number>)`. `<number>` can be `0 - 255` or `0% to 100%` and `<hex>` can be `#FFF` or `#FFFFFF`.
        """

        if not operation:
            await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=str(ctx.guild_config.colour).upper()))
            return

        if await self.bot.is_owner(ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        old_colour = ctx.guild_config.colour

        if operation == 'reset':
            await self.bot.guild_manager.set_colour(guild_id=ctx.guild.id)

        elif operation == 'set':

            if not colour:
                raise exceptions.ArgumentError(f'You did not provide a valid colour argument. See `{config.PREFIX}help settings colour` for possible formats.')
            if colour == ctx.guild_config.colour:
                raise exceptions.ArgumentError(f'This servers embed colour is already `{str(colour).upper()}`.')

            await self.bot.guild_manager.set_colour(guild_id=ctx.guild.id, colour=str(colour))

        await ctx.send(embed=discord.Embed(colour=old_colour, title=f'Old: {str(old_colour).upper()}'))
        await ctx.send(embed=discord.Embed(colour=ctx.guild_config.colour, title=f'New: {str(ctx.guild_config.colour).upper()}'))

    @settings.command(name='embed-size', aliases=['embedsize', 'es'])
    async def config_embed_size(self, ctx: context.Context, operation: Literal['set', 'reset'] = None, size: Literal['large', 'medium', 'small'] = None) -> None:
        """
        Manage this servers embed size settings.

        Please note that to view the the current size, no permissions are needed, however to change it you require the `manage_guild` permission.

        `operation`: The operation to perform, `set` to change it or `reset` to revert it to the default. If not provided the current size will be displayed.
        `size`: The size to set embeds too. Can be `large`, `medium` or `small`.
        """

        if not operation:
            await ctx.send(f'This servers embed size is `{ctx.guild_config.embed_size.name.title()}`.')

        if await self.bot.is_owner(ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        if operation == 'set':

            if not size:
                raise exceptions.ArgumentError('You did not provide a valid size. Available sizes are `large`, `medium` or `small`.')

            await self.bot.guild_manager.set_embed_size(guild_id=ctx.guild.id, embed_size=getattr(enums.EmbedSize, size.upper()))
            await ctx.send(f'Set this servers embed size to `{size.title()}`.')

        elif operation == 'reset':

            await self.bot.guild_manager.set_embed_size(guild_id=ctx.guild.id)
            await ctx.send('Set this servers embed size to `Large`.')

    @settings.command(name='prefix', aliases=['prefixes'])
    async def config_prefix(self, ctx: context.Context, operation: Literal['add', 'remove', 'reset', 'clear'] = None, prefix: converters.PrefixConverter = None) -> None:
        """
        Manage this servers prefix settings.

        Please note that to view the prefixes, no permissions are needed, however to change them you require the `manage_guild` permission.

        `operation`: The operation to perform, `add` to add a prefix, `remove` to remove one, `reset` or `clear` to remove them all. If not provided a list of current prefixes will be displayed.
        `prefix`: The prefix to add or remove. Must be less than 15 characters.
        """

        if not operation:
            prefixes = await self.bot.get_prefix(ctx.message)
            clean_prefixes = [f'`1.` {prefixes[0]}', *[f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:])]]
            await ctx.paginate_embed(entries=clean_prefixes, per_page=10, colour=ctx.guild_config.colour, title='List of usable prefixes.')
            return

        if await self.bot.is_owner(ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        if operation == 'add':

            if not prefix:
                raise exceptions.ArgumentError('You did not provide a prefix to add. Valid prefixes are less then 15 characters and contain no backtick `\`` characters.')

            if len(ctx.guild_config.prefixes) > 20:
                raise exceptions.ArgumentError('This server can not have more than 20 custom prefixes.')
            if prefix in ctx.guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server already has the prefix `{prefix}`.')

            await self.bot.guild_manager.set_prefixes(guild_id=ctx.guild.id, prefix=str(prefix))
            await ctx.send(f'Added `{prefix}` to this servers prefixes.')

        elif operation == 'remove':

            if not prefix:
                raise exceptions.ArgumentError('You did not provide a prefix to remove. Valid prefixes are less then 15 characters and contain no backtick (`) characters.')

            if prefix not in ctx.guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server does not have the prefix `{prefix}`.')

            await self.bot.guild_manager.set_prefixes(guild_id=ctx.guild.id, operation=enums.Operation.REMOVE, prefix=str(prefix))
            await ctx.send(f'Removed `{prefix}` from this servers prefixes.')

        elif operation in {'reset', 'clear'}:

            if not ctx.guild_config.prefixes:
                raise exceptions.ArgumentError('This server does not have any custom prefixes.')

            await self.bot.guild_manager.set_prefixes(guild_id=ctx.guild.id, operation=enums.Operation.RESET)
            await ctx.send('Cleared this servers prefixes.')


def setup(bot: Life):
    bot.add_cog(Settings(bot))
