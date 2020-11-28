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
import asyncio
import typing

import discord
import pendulum
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions
from utilities.enums import Editables, Operations


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.bot.dateparser_settings = {
            'DATE_ORDER': 'DMY',
            'TIMEZONE': 'UTC',
            'RETURN_AS_TIMEZONE_AWARE': False,
            'PREFER_DAY_OF_MONTH': 'current',
            'PREFER_DATES_FROM': 'future',
            'PARSERS': ['relative-time', 'absolute-time', 'timestamp', 'custom-formats']
        }

    @commands.command(name='timezones', aliases=['tzs'])
    async def timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(entries=pendulum.timezones, per_page=20, title='Available timezones:')

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
                    if user_config.timezone_private is True and member.id != ctx.author.id:
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

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone, operation=Operations.set, value=timezone.name)
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @time.command(name='reset', aliases=['clear', 'default'])
    async def time_reset(self, ctx: context.Context) -> None:
        """
        Sets your timezone back to the default (UTC)
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone, operation=Operations.reset)
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @time.command(name='private')
    async def time_private(self, ctx: context.Context) -> None:
        """
        Toggles your timezone being private or public.
        """

        if ctx.user_config.timezone_private is False:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone_private, operation=Operations.set)
            await ctx.send('Your timezone is now private.')
        else:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone_private, operation=Operations.reset)
            await ctx.send('Your timezone is now public.')

    @commands.command(name='timecard')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all the servers members.
        """

        async with ctx.typing():
            buffer = await self.bot.user_manager.create_timecard(guild_id=ctx.guild.id)
            await ctx.send(file=discord.File(fp=buffer, filename='timecard.png'))

    @commands.group(name='reminders', aliases=['remind', 'reminder', 'remindme'])
    async def reminders(self, ctx: context.Context, *, reminder: converters.DatetimeParser = None) -> None:
        """
        Schedules a reminder for the given time with the text.
        """

        if reminder is not None:

            if len(reminder['found'].keys()) > 1:

                entries = [(datetime_phrase, datetime) for datetime_phrase, datetime in reminder['found'].items()]

                paginator = await ctx.paginate_embed(entries=[
                    f'`{index + 1}.` **{datetime_phrase}**\n`{self.bot.utils.format_datetime(datetime=datetime)}`' for index, (datetime_phrase, datetime) in enumerate(entries)
                ], per_page=10, header=f'**Multiple time and/or dates were detected within your query, please select the one you would like to be reminded at:**\n\n')

                try:
                    response = await self.bot.wait_for('message', check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30.0)
                except asyncio.TimeoutError:
                    raise exceptions.ArgumentError('You took too long to respond.')

                response = await commands.clean_content().convert(ctx=ctx, argument=response.content)
                try:
                    response = int(response) - 1
                except ValueError:
                    raise exceptions.ArgumentError('That was not a valid number.')
                if response < 0 or response >= len(entries):
                    raise exceptions.ArgumentError('That was not one of the available options.')

                await paginator.stop()
                result = tuple(entries[response])

            else:
                result = tuple(reminder['found'].items())

            datetime = self.bot.utils.format_datetime(datetime=result[0][1], seconds=True)
            datetime_difference = self.bot.utils.format_difference(datetime=result[0][1], suppress=[])

            await self.bot.user_manager.remind_manager.create_reminder(user_id=ctx.author.id, datetime=result[0][1], content=reminder['argument'], ctx=ctx)
            await ctx.send(f'Set a reminder for `{datetime}`, `{datetime_difference}` from now.')
            return

        await ctx.invoke(self.reminders_list)

    @reminders.command(name='list')
    async def reminders_list(self, ctx: context.Context) -> None:
        pass


def setup(bot):
    bot.add_cog(Time(bot))
