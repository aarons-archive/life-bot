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

from typing import Literal, Optional

from discord.ext import commands

import colours
from bot import Life
from utilities import context, converters, enums, exceptions


class Settings(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name='settings', aliases=['config'], invoke_without_command=True)
    async def settings(self, ctx: context.Context) -> None:
        pass

    #

    @settings.group(name='user', invoke_without_command=True)
    async def settings_user(self, ctx: context.Context) -> None:
        pass

    #

    @settings.group(name='guild', invoke_without_command=True)
    async def settings_guild(self, ctx: context.Context) -> None:
        pass

    @settings_guild.command(name='embed-size', aliases=['embedsize', 'es'])
    async def settings_guild_embed_size(self, ctx: context.Context, operation: Optional[Literal['set', 'reset']], size: Optional[Literal['large', 'medium', 'small']]) -> None:
        """
        Manage this servers embed size settings.

        Please note that to view the current size, no permissions are needed, however to change it you require the `manage_guild` permission.

        `operation`: The operation to perform, `set` to change it or `reset` to revert it to the default. If not provided the current size will be displayed.
        `size`: The size to set embeds too. Can be `large`, `medium` or `small`.
        """

        if not operation:
            await ctx.reply(f'This servers embed size is `{ctx.guild_config.embed_size.name.title()}`.')
            return

        if await self.bot.is_owner(user=ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        guild_config = await self.bot.guild_manager.get_or_create_config(ctx.guild.id)

        if operation == 'reset':

            if guild_config.embed_size == enums.EmbedSize.LARGE:
                raise exceptions.ArgumentError('This servers embed size is already the default.')

            await guild_config.set_embed_size()
            await ctx.reply('Reset this servers embed size.')

        elif operation == 'set':

            if not size:
                raise exceptions.ArgumentError('You did not provide a valid size.')
            if guild_config.embed_size == getattr(enums.EmbedSize, size.upper()):
                raise exceptions.ArgumentError(f'This servers embed size is already `{guild_config.embed_size.name.title()}`.')

            await guild_config.set_embed_size(getattr(enums.EmbedSize, size.upper()))
            await ctx.reply(f'Set this servers embed size to `{guild_config.embed_size.name.title()}`.')

    @settings_guild.command(name='prefix', aliases=['prefixes'])
    async def settings_guild_prefix(self, ctx: context.Context, operation: Optional[Literal['add', 'remove', 'reset', 'clear']], prefix: Optional[converters.PrefixConverter]) -> None:
        """
        Manage this servers prefix settings.

        Please note that to view the prefixes, no permissions are needed, however to change them you require the `manage_guild` permission.

        `operation`: The operation to perform, `add` to add a prefix, `remove` to remove one, `reset` or `clear` to remove them all. If not provided a list of current prefixes will be displayed.
        `prefix`: The prefix to add or remove. Must be less than 15 characters.
        """

        if not operation:
            prefixes = await self.bot.get_prefix(ctx.message)
            clean_prefixes = [f'`1.` {prefixes[0]}', *[f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:])]]
            await ctx.paginate_embed(entries=clean_prefixes, per_page=10, colour=colours.MAIN, title='List of usable prefixes.')
            return

        if await self.bot.is_owner(ctx.author) is False:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx=ctx)

        guild_config = await self.bot.guild_manager.get_or_create_config(ctx.guild.id)

        if operation == 'add':

            if not prefix:
                raise exceptions.ArgumentError('You did not provide a prefix to add.')
            if prefix in guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server already has the prefix `{prefix}`.')

            if len(guild_config.prefixes) > 20:
                raise exceptions.ArgumentError('This server can not have more than 20 custom prefixes.')

            await guild_config.change_prefixes(enums.Operation.ADD, prefix=str(prefix))
            await ctx.reply(f'Added `{prefix}` to this servers prefixes.')

        elif operation == 'remove':

            if not prefix:
                raise exceptions.ArgumentError('You did not provide a prefix to remove.')
            if prefix not in guild_config.prefixes:
                raise exceptions.ArgumentError(f'This server does not have the prefix `{prefix}`.')

            await guild_config.change_prefixes(enums.Operation.REMOVE, prefix=str(prefix))
            await ctx.reply(f'Removed `{prefix}` from this servers prefixes.')

        elif operation in {'reset', 'clear'}:

            if not guild_config.prefixes:
                raise exceptions.ArgumentError('This server does not have any custom prefixes.')

            await guild_config.change_prefixes(enums.Operation.RESET)
            await ctx.reply('Cleared this servers prefixes.')


def setup(bot: Life) -> None:
    bot.add_cog(Settings(bot=bot))
