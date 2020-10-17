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
import pendulum
import wolframalpha
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.bot.wolframalpha = wolframalpha.Client(self.bot.config.wolframalpha_token)

    @commands.command(name='timezones', aliases=['tzs'])
    async def timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(entries=pendulum.timezones, per_page=20, title='Available timezones:', url=f'{self.bot.dashboard}timezones')

    @commands.group(name='time', invoke_without_command=True)
    async def time(self, ctx: context.Context, *, timezone: str = None) -> None:
        """
        Displays the time of the member or the timezone provided.

        `timezone`: The timezone or members name, id or mention that you want to get.
        """

        if not timezone:
            member = ctx.author
            timezone = ctx.user_config.timezone

        else:
            try:
                member = None
                timezone = await converters.TimezoneConverter().convert(ctx=ctx, argument=timezone)

            except exceptions.ArgumentError as error:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=timezone)
                    user_config = self.bot.user_manager.get_user_config(user_id=member.id)
                    if user_config.timezone_private is True and not member.id == ctx.author.id:
                        raise exceptions.ArgumentError('That users timezone is private.')
                    timezone = user_config.timezone
                except commands.BadArgument:
                    raise exceptions.ArgumentError(str(error))

        datetime = self.bot.utils.format_datetime(datetime=pendulum.now(tz=timezone))

        embed = discord.Embed(colour=ctx.colour, title=f'Time in {timezone.name} {f"({member})" if member else ""}', description=f'```py\n{datetime}\n```')
        await ctx.send(embed=embed)

    @time.command(name='set')
    async def time_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone to the one specified.

        See https://dashboard.mrrandom.xyz/timezones for a full list of available timezones.

        `timezone`: The timezone to use.
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, attribute='timezone', operation='set', value=timezone.name)
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @time.command(name='reset', aliases=['clear', 'default'])
    async def time_reset(self, ctx: context.Context) -> None:
        """
        Sets your timezone back to the default (UTC)
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, attribute='timezone', operation='reset')
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @time.command(name='private')
    async def time_private(self, ctx: context.Context) -> None:
        """
        Toggles your timezone being private or public.
        """

        if ctx.user_config.timezone_private is False:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, attribute='timezone_private', operation='set')
            await ctx.send('Your timezone is now private.')
        else:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, attribute='timezone_private', operation='reset')
            await ctx.send('Your timezone is now public.')

    @commands.command(name='timecard')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all the servers members.
        """

        async with ctx.typing():
            buffer = await self.bot.user_manager.create_timecard(guild_id=ctx.guild.id)
            await ctx.send(file=discord.File(fp=buffer, filename='timecard.png'))


def setup(bot):
    bot.add_cog(Time(bot))
