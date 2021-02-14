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

import config
from bot import Life
from utilities import context, converters, exceptions, utils
from utilities.enums import Editables, Operations


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='time')
    async def time(self, ctx: context.Context, *, timezone: str = None) -> None:
        """
        Displays the time of the member or timezone provided.

        `timezone`: The timezone or members Name, Nickname, ID, or @Mention that you want to get.
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

        datetime = utils.format_datetime(datetime=pendulum.now(tz=timezone))

        embed = discord.Embed(colour=ctx.colour, title=f'Time in {timezone.name}{f" ({member})" if member else ""}:', description=f'```py\n{datetime}\n```')
        await ctx.send(embed=embed)

    @commands.command(name='times')
    async def times(self, ctx: context.Context) -> None:

        configs = sorted(self.bot.user_manager.configs.items(), key=lambda kv: kv[1].time.offset_hours)
        timezone_users = {}

        for user_id, user_config in configs:

            member = ctx.guild.get_member(user_id)
            if not member:
                continue

            if user_config.timezone_private or user_config.timezone == pendulum.timezone('UTC'):
                continue

            if timezone_users.get(user_config.time.format('HH:mm (ZZ)')) is None:
                timezone_users[user_config.time.format('HH:mm (ZZ)')] = [f'{member} - {user_config.timezone.name}']
            else:
                timezone_users[user_config.time.format('HH:mm (ZZ)')].append(f'{member} - {user_config.timezone.name}')

        if not timezone_users:
            raise exceptions.ArgumentError('There are no users with timezones set.')

        entries = [f'`{timezone}:`\n{config.NL.join(members)}\n' for timezone, members in timezone_users.items()]
        await ctx.paginate_embed(entries=entries, per_page=5, header='**User timezones:**\n\n')

    @commands.command(name='timecard')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all the servers members.
        """

        async with ctx.typing():
            buffer = await self.bot.user_manager.create_timecard(guild_id=ctx.guild.id)
            await ctx.send(file=discord.File(fp=buffer, filename='timecard.png'))

    #

    @commands.group(name='timezone', aliases=['timezones', 'tzs', 'tz'], invoke_without_command=True)
    async def _timezone(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(entries=pendulum.timezones, per_page=20,
                                 header='**Available timezones:**\nClick [here](https://skeletonclique.mrrandom.xyz/timezones) to view a list of timezones.\n\n')

    @_timezone.command(name='set')
    async def _timezone_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone to the one specified.

        `timezone`: The timezone to use. See `!timezones` for a list of timezones.
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone, operation=Operations.set, value=timezone.name)
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @_timezone.command(name='reset', aliases=['default'])
    async def _timezone_reset(self, ctx: context.Context) -> None:
        """
        Sets your timezone back to the default (UTC).
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone, operation=Operations.reset)
        await ctx.send(f'Your timezone has been set to `{ctx.user_config.timezone.name}`.')

    @_timezone.command(name='private')
    async def _timezone_private(self, ctx: context.Context) -> None:
        """
        Sets your timezone to be private.
        """

        if ctx.user_config.timezone_private is True:
            raise exceptions.ArgumentError('Your timezone is already private.')

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone_private, operation=Operations.set)
        await ctx.send('Your timezone is now private.')

    @_timezone.command(name='public')
    async def _timezone_public(self, ctx: context.Context) -> None:
        """
        Sets your timezone to be public.
        """

        if ctx.user_config.timezone_private is False:
            raise exceptions.ArgumentError('Your timezone is already public.')

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.timezone_private, operation=Operations.reset)
        await ctx.send('Your timezone is now public.')

    #

    @commands.group(name='reminders', aliases=['remind', 'reminder', 'remindme'], invoke_without_command=True)
    async def reminders(self, ctx: context.Context, *, reminder: converters.DatetimeConverter) -> None:
        """
        Schedules a reminder for the given time with the text.

        `reminder`: The content of reminder, should include some form of date or time such as `tomorrow`, `in 12h` or `1st january 2020`.
        """

        entries = {index: (datetime_phrase, datetime) for index, (datetime_phrase, datetime) in enumerate(reminder['found'].items())}

        if len(entries) != 1:
            choice = await ctx.paginate_choice(
                     entries=[f'`{index + 1}.` **{phrase}**\n`{utils.format_datetime(datetime=datetime)}`' for index, (phrase, datetime) in entries.items()],
                     per_page=10, header=f'**Multiple times/dates were detected within your query, please select the one you would like to be reminded at:**\n\n'
            )
            result = entries[choice]
        else:
            result = entries[0]

        datetime = utils.format_datetime(datetime=result[1], seconds=True)
        datetime_difference = utils.format_difference(datetime=result[1], suppress=[])

        await self.bot.reminder_manager.create_reminder(user_id=ctx.author.id, datetime=result[1], content=reminder['argument'], ctx=ctx)
        await ctx.send(f'Set a reminder for `{datetime}`, `{datetime_difference}` from now.')

    @reminders.command(name='list')
    async def reminders_list(self, ctx: context.Context) -> None:
        """
        Displays a list of your reminders.
        """

        reminders = [reminder for reminder in ctx.user_config.reminders if not reminder.done]

        if not reminders:
            raise exceptions.ArgumentError('You do not have any active reminders.')

        entries = [
            f'`{reminder.id}:` **In {utils.format_difference(datetime=reminder.datetime, suppress=[])}**\n'
            f'`When:` {utils.format_datetime(datetime=reminder.datetime, seconds=True)}\n'
            f'`Content:` {reminder.content[:100]}\n'
            for reminder in sorted(reminders, key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(entries=entries, per_page=5, header=f'**Reminders for** `{ctx.author}:`\n\n')

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

            reminder = await self.bot.reminder_manager.get_reminder(user_id=ctx.author.id, reminder_id=reminder_id)
            if not reminder:
                raise exceptions.ArgumentError(f'You do not have a reminder with the id `{reminder_id}`.')

            if reminder.id in reminder_ids_to_remove:
                raise exceptions.ArgumentError(f'You provided the reminder id `{reminder.id}` more than once.')

            reminder_ids_to_remove.append(reminder.id)

        for reminder_id in reminder_ids_to_remove:
            await self.bot.reminder_manager.delete_reminder(user_id=ctx.author.id, reminder_id=reminder_id)

        s = 's' if len(reminder_ids_to_remove) > 1 else ''
        await ctx.send(f'Deleted {len(reminder_ids_to_remove)} reminder{s} with id{s} {", ".join(f"`{reminder_id}`" for reminder_id in reminder_ids_to_remove)}.')


def setup(bot: Life):
    bot.add_cog(Time(bot))
