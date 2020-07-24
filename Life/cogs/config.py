"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from discord.ext import commands
import asyncio

from cogs.utilities import exceptions, checks
from utilities.context import Context


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.load_task = asyncio.create_task(self.load())

    async def load(self):

        await self.bot.wait_until_ready()

        prefixes = await self.bot.db.fetch('SELECT * FROM prefixes')
        for guild in prefixes:
            self.bot.prefixes[guild['server_id']] = sorted(guild['prefixes'], key=lambda prefix: prefix.endswith(' '))
        print(f'[POSTGRESQL] Loaded guild prefixes. [{len(prefixes)} guild(s)]')

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx: Context):
        """
        Displays a list of prefixes available in the current server.
        """
        prefixes = await self.bot.get_prefix(ctx.message)
        entries = [f'`1.` {prefixes[1]}']
        entries.extend(f'`{index + 2}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:]))
        return await ctx.paginate_embed(entries=entries, entries_per_page=10, title=f'List of usable prefixes in {ctx.guild}.')

    @prefix.command(name='add')
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_add(self, ctx: Context, prefix: commands.clean_content):
        """
        Adds a prefix to the server.

        Please note that adding a prefix such as `!` and then `!?` will not work as commands will try to match with the first one.

        `prefix`: The prefix to add.
        """

        if len(str(prefix)) > 20:
            raise exceptions.ArgumentError(f'Prefixes can not be more than 20 characters long.')
        if '`' in prefix:
            raise exceptions.ArgumentError(f'Prefixes can not contain backtick characters.')

        guild_prefixes = await self.bot.db.fetchrow('SELECT * FROM prefixes WHERE server_id = $1', ctx.guild.id)
        if not guild_prefixes:
            self.bot.prefixes[ctx.guild.id] = [prefix]
            await self.bot.db.execute('INSERT INTO prefixes values ($1, array[$2])', ctx.guild.id, prefix)
            return await ctx.send(f'Added `{prefix}` to this servers prefixes.')

        if prefix in guild_prefixes['prefixes']:
            raise exceptions.ArgumentError(f'This server already has the `{prefix}` prefix.')
        if len(guild_prefixes['prefixes']) > 10:
            raise exceptions.ArgumentError(f'This server can only have up to 10 prefixes.')

        self.bot.prefixes[ctx.guild.id].append(prefix)
        await self.bot.db.execute('UPDATE prefixes SET prefixes = array_append(prefixes.prefixes, $1) WHERE server_id = $2', prefix, ctx.guild.id)
        return await ctx.send(f'Added `{prefix}` to this servers prefixes.')

    @prefix.command(name='delete', aliases=['remove'])
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_delete(self, ctx: Context, prefix: commands.clean_content):
        """
        Deletes a prefix from the server.

        `prefix`: The prefix to delete.
        """

        if len(str(prefix)) > 20:
            raise exceptions.ArgumentError(f'Prefixes can not be more than 20 characters long.')
        if '`' in prefix:
            raise exceptions.ArgumentError(f'Prefixes can not contain backtick characters.')

        guild_prefixes = await self.bot.db.fetchrow('SELECT * FROM prefixes WHERE server_id = $1', ctx.guild.id)
        if prefix not in guild_prefixes['prefixes']:
            raise exceptions.ArgumentError(f'This server does not have the `{prefix}` prefix.')

        self.bot.prefixes[ctx.guild.id].remove(prefix)
        await self.bot.db.execute('UPDATE prefixes SET prefixes = array_remove(prefixes.prefixes, $1) WHERE server_id = $2', prefix, ctx.guild.id)
        return await ctx.send(f'Removed `{prefix}` from this servers prefixes.')

    @prefix.command(name='clear')
    @checks.has_guild_permissions(manage_guild=True)
    async def prefix_clear(self, ctx: Context):
        """
        Clear all prefixes from the server.
        """

        guild_prefixes = await self.bot.db.fetchrow('SELECT * FROM prefixes WHERE server_id = $1', ctx.guild.id)
        if not guild_prefixes:
            raise exceptions.ArgumentError('This server has no customizable prefixes.')

        del self.bot.prefixes[ctx.guild.id]
        await self.bot.db.execute('DELETE FROM prefixes WHERE server_id = $1', ctx.guild.id)
        return await ctx.send(f'Cleared this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
