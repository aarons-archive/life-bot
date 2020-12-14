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
        await ctx.paginate_embed(entries=pendulum.timezones, per_page=25, title='Available timezones:')

    #

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

        datetime = self.bot.utils.format_datetime(datetime=pendulum.now(tz=timezone), seconds=True)

        embed = discord.Embed(colour=ctx.colour, title=f'Time in {timezone.name} {f"({member})" if member else ""}', description=f'```py\n{datetime}\n```')
        await ctx.send(embed=embed)

    @time.command(name='set')
    async def time_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone to the one specified.

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

    #

    @commands.command(name='timecard')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all the servers members.
        """

        async with ctx.typing():
            buffer = await self.bot.user_manager.create_timecard(guild_id=ctx.guild.id)
            await ctx.send(file=discord.File(fp=buffer, filename='timecard.png'))

    #

    @commands.group(name='reminders', aliases=['remind', 'reminder', 'remindme'], invoke_without_command=True)
    async def reminders(self, ctx: context.Context, *, reminder: converters.DatetimeConverter) -> None:
        """
        Schedules a reminder for the given time with the text.

        `reminder`: The content of reminder, should include some form of date or time such as `tomorrow`, `in 12h` or `1st january 2020`.
        """

        entries = {index: (datetime_phrase, datetime) for index, (datetime_phrase, datetime) in enumerate(reminder['found'].items())}

        if len(entries) != 1:
            result = await ctx.paginate_choice(
                    entries=[f'`{index + 1}.` **{phrase}**\n`{self.bot.utils.format_datetime(datetime=datetime)}`' for index, (phrase, datetime) in entries.items()],
                    per_page=10, header=f'**Multiple times/dates were detected within your query, please select the one you would like to be reminded at:**\n\n'
            )

        else:
            result = entries[0]

        datetime = self.bot.utils.format_datetime(datetime=result[1], seconds=True)
        datetime_difference = self.bot.utils.format_difference(datetime=result[1], suppress=[])

        await self.bot.user_manager.remind_manager.create_reminder(user_id=ctx.author.id, datetime=result[1], content=reminder['argument'], ctx=ctx)
        await ctx.send(f'Set a reminder for `{datetime}`, `{datetime_difference}` from now.')

    @reminders.command(name='list')
    async def reminders_list(self, ctx: context.Context) -> None:
        """
        Displays a list of your reminders.
        """

        reminders = [reminder for reminder in ctx.user_config.reminders if not reminder.done]

        if not reminders:
            raise exceptions.GeneralError('You do not have any active reminders.')

        embed = discord.Embed(colour=ctx.colour, description=f'**Reminders for** `{ctx.author}:`\n\n')

        for reminder in sorted(reminders, key=lambda reminder: reminder.datetime):

            embed.description += f'`{reminder.id}`: **In {self.bot.utils.format_difference(datetime=reminder.datetime, suppress=[])}**\n' \
                                 f'`When:` {self.bot.utils.format_datetime(datetime=reminder.datetime, seconds=True)}\n' \
                                 f'`Content:` {reminder.content[:100]}\n\n'

        await ctx.send(embed=embed)

    @reminders.command(name='delete', aliases=['remove'])
    async def reminders_delete(self, ctx: context.Context, *, reminder_ids: str) -> None:
        """
        Deletes the reminder(s) with the given ID(s).

        `reminder_ids`: A list of reminders IDs to delete, separated by spaces.
        """

        reminder_ids_to_remove = []

        for reminder_id in reminder_ids.split(' '):

            try:
                reminder_id = int(reminder_id)
            except ValueError:
                raise exceptions.ArgumentError(f'`{reminder_id}` is not a valid reminder id.')

            reminder = await self.bot.user_manager.remind_manager.get_reminder(user_id=ctx.author.id, reminder_id=reminder_id)
            if not reminder:
                raise exceptions.ArgumentError(f'You do not have a reminder with the id `{reminder_id}`.')

            if reminder.id in reminder_ids_to_remove:
                raise exceptions.ArgumentError(f'You provided the reminder id `{reminder.id}` more than once.')

            reminder_ids_to_remove.append(reminder.id)

        for reminder_id in reminder_ids_to_remove:
            await self.bot.user_manager.remind_manager.delete_reminder(user_id=ctx.author.id, reminder_id=reminder_id)

        s = "s" if len(reminder_ids_to_remove) > 1 else ""
        await ctx.send(f'Deleted {len(reminder_ids_to_remove)} reminder{s} with id{s} {", ".join(f"`{reminder_id}`" for reminder_id in reminder_ids_to_remove)}.')


def setup(bot: Life):
    bot.add_cog(Time(bot))
