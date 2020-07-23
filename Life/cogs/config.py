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

from cogs.utilities import exceptions


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.load_task = asyncio.create_task(self.load())

    async def load(self):

        await self.bot.wait_until_ready()

        prefixes = await self.bot.db.fetch('SELECT * FROM prefixes')
        for guild in prefixes:
            self.bot.prefixes[guild['server_id']] = guild['prefixes']
        print(f'[POSTGRESQL] Loaded guild prefixes. [{len(prefixes)} guild(s)]')

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """
        Displays a list of prefixes available in the current server.
        """
        title = f'List of usable prefixes in {ctx.guild}.'
        prefixes = await self.bot.get_prefix(ctx.message)
        entries = [f'`1.` {prefixes[1]}']
        entries.extend(f'`{index + 1}.` `{prefix}`' for index, prefix in enumerate(prefixes[2:]))
        return await ctx.paginate_embed(entries=entries,  title=title, entries_per_page=10)

    @prefix.command(name='add')
    async def prefix_add(self, ctx, *, prefix: commands.clean_content):
        """
        Adds a prefix to the current server.

        `prefix`: The prefix to add, must be up to 20 characters and not have any ` characters.
        """

        prefixes = await self.bot.db.fetchrow('SELECT * FROM prefixes WHERE server_id = $1', ctx.guild.id)
        if prefix in prefixes['prefixes']:
            raise exceptions.ArgumentError(f'The prefix `{prefix}` is already used in this server.')

        if len(prefixes['prefixes']) > 20:
            raise exceptions.ArgumentError(f'You can only have upto 20 prefixes per server.')
        if len(str(prefix)) > 20:
            raise exceptions.ArgumentError(f'Prefix can not be more than 20 characters long.')
        if '`' in prefix:
            raise exceptions.ArgumentError(f'Prefixes can not contain backtick characters.')

        self.bot.prefixes[ctx.guild.id].append(prefix)
        await self.bot.db.execute('UPDATE prefixes SET prefixes = array_append(prefixes.prefixes, $1) WHERE server_id = $2', prefix, ctx.guild.id)
        return await ctx.send(f'Added `{prefix}` to this servers prefixes.')


def setup(bot):
    bot.add_cog(Config(bot))
