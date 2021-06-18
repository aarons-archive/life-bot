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

from typing import Optional

import discord
import pendulum
import rapidfuzz
from discord.ext import commands
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone

import config
from bot import Life
from utilities import context, converters, exceptions, utils


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='times')
    async def times(self, ctx: context.Context) -> None:
        """
        Displays a list of people and what timezone they are in.
        """

        if not (timezones := self.bot.user_manager.timezones(guild_id=getattr(ctx.guild, 'id', None))):
            raise exceptions.ArgumentError('There are no users who have set their timezone, or everyone has set them to be private.')

        timezone_users = {}

        for user_config in timezones:

            user = ctx.guild.get_member(user_config.id) if ctx.guild else self.bot.get_user(user_config.id)
            timezone = user_config.time.format('HH:mm (ZZ)')

            if users := timezone_users.get(timezone, []):
                if len(users) > 36:
                    break
                timezone_users[timezone].append(f'{user} - {user_config.timezone.name}')
            else:
                timezone_users[timezone] = [f'{user} - {user_config.timezone.name}']

        entries = [f'`{timezone}:`\n{config.NL.join(members)}\n' for timezone, members in timezone_users.items()]
        await ctx.paginate_embed(entries=entries, per_page=5, title=f'{ctx.guild}\'s timezones:')

    @commands.command(name='timezones', aliases=['tzs'])
    async def _timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(
                entries=list(pendulum.timezones), per_page=20,
                title='Available timezones:', header='Click [here](https://skeletonclique.mrrandom.xyz/timezones) to view a list of timezones.\n\n'
        )

    #

    @commands.group(name='timezone', aliases=['time'], invoke_without_command=True)
    async def _timezone(self, ctx: context.Context, *, timezone: Optional[str]) -> None:
        """
        Displays the time of the member or timezone provided.

        `timezone`: The timezone or members Name, Nickname, ID, or @Mention that you want to get.
        """

        member: Optional[discord.Member] = None

        if not timezone:
            member = ctx.author
            found_timezone = ctx.user_config.timezone
        else:
            try:
                found_timezone = pendulum.timezone(timezone)
            except InvalidTimezone:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=timezone)
                except commands.BadArgument:
                    msg = '\n'.join(f'- `{match}`' for match, _, _ in rapidfuzz.process.extract(query=timezone, choices=pendulum.timezones, processor=lambda s: s))
                    raise exceptions.ArgumentError(f'I did not recognise that timezone or member. Maybe you meant one of these?\n{msg}')
                else:
                    if (user_config := self.bot.user_manager.get_config(member.id)).timezone_private is True and member.id != ctx.author.id:
                        raise exceptions.ArgumentError('That users timezone is private.')
                    found_timezone = user_config.timezone

        if not found_timezone:
            raise exceptions.ArgumentError('That user has not set their timezone.')

        embed = discord.Embed(
                colour=config.MAIN,
                title=f'Time in `{found_timezone.name}`{f" for `{member}`" if member else ""}:',
                description=f'```\n{utils.format_datetime(pendulum.now(tz=found_timezone))}\n```'
        )
        await ctx.reply(embed=embed)

    @_timezone.command(name='card')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all servers members.
        """

        async with ctx.typing():
            file = await self.bot.user_manager.create_timecard(guild_id=getattr(ctx.guild, 'id', None))
            await ctx.reply(file=file)

    @_timezone.command(name='set')
    async def _timezone_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone.

        `timezone`: The timezone to use. See [here](https://skeletonclique.mrrandom.xyz/timezones) for a list of timezones in an easier to navigate format.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        # noinspection PyTypeChecker
        await user_config.set_timezone(timezone)
        await ctx.reply(f'Your timezone has been set to `{user_config.timezone.name}`.')

    @_timezone.command(name='reset')
    async def _timezone_reset(self, ctx: context.Context) -> None:
        """
        Resets your timezone information.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        await user_config.set_timezone(pendulum.timezone('UTC'))
        await ctx.reply(f'Your timezone has been reset back to `{user_config.timezone.name}`.')

    @_timezone.command(name='private')
    async def _timezone_private(self, ctx: context.Context) -> None:
        """
        Make your timezone private.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if user_config.timezone_private is True:
            raise exceptions.ArgumentError('Your timezone is already private.')

        await user_config.set_timezone(user_config.timezone, private=True)
        await ctx.reply('Your timezone is now private.')

    @_timezone.command(name='public')
    async def _timezone_public(self, ctx: context.Context) -> None:
        """
        Make your timezone public.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if user_config.timezone_private is False:
            raise exceptions.ArgumentError('Your timezone is already public.')

        await user_config.set_timezone(user_config.timezone, private=False)
        await ctx.reply('Your timezone is now public.')

    #

    @commands.group(name='reminders', aliases=['remind', 'reminder', 'remindme'], invoke_without_command=True)
    async def reminders(self, ctx: context.Context, *, time: converters.DatetimeConverter) -> None:
        """
        Schedule a reminder for the given time.

        `time`: The content of reminder, should include some form of date or time such as `tomorrow`, `in 12h` or `1st january 2020`.
        """

        entries = {index: (datetime_phrase, datetime) for index, (datetime_phrase, datetime) in enumerate(time['found'].items())}
        if len(entries) != 1:
            choice = await ctx.choice(
                     entries=[f'`{index + 1}.` **{phrase}**\n`{utils.format_datetime(datetime)}`' for index, (phrase, datetime) in entries.items()],
                     per_page=10, title='Multiple datetimes were detected within your query:', header='Please select the number that best matches your intention:\n\n'
            )
            result = entries[choice]
        else:
            result = entries[0]

        content = await utils.safe_content(self.bot.mystbin, time['argument'], max_characters=1500)

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)
        reminder = await user_config.create_reminder(channel_id=ctx.channel.id, datetime=result[1], content=content, jump_url=ctx.message.jump_url)

        datetime = utils.format_datetime(reminder.datetime, seconds=True)
        datetime_difference = utils.format_difference(reminder.datetime, suppress=[])
        await ctx.reply(f'Created a reminder with ID `{reminder.id}` for `{datetime}`, `{datetime_difference}` from now.')

    @reminders.command(name='edit')
    async def reminders_edit(self, ctx: context.Context, reminder_id: int, *, content: str) -> None:
        """
        Edit a reminders content.

        `reminder_id`: The id of the reminder to edit.
        `content`: The content to edit the reminder with.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.ArgumentError('You do not have a reminder with that id.')

        content = await utils.safe_content(self.bot.mystbin, content, max_characters=1500)
        await reminder.change_content(content, jump_url=ctx.message.jump_url)

        await ctx.reply(f'Edited content of reminder with id `{reminder.id}`.')

    @reminders.group(name='repeat')
    async def reminder_repeat(self, ctx: context.Context, reminder_id: int, *, repeat_type: converters.ReminderRepeatTypeConverter) -> None:
        """
        Edit a reminders repeat type.

        `reminder_id`: The id of the reminder to edit.
        `content`: The repeat type to set on the reminder.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.ArgumentError('You do not have a reminder with that id.')

        # noinspection PyTypeChecker
        await reminder.change_repeat_type(repeat_type)
        await ctx.reply(f'Edited repeat type of reminder with id `{reminder.id}`.')

    @reminders.command(name='delete')
    async def reminders_delete(self, ctx: context.Context, reminder_ids: commands.Greedy[int]) -> None:
        """
        Delete reminders with the given id's.

        `reminder_ids`: A list of reminders id's to delete, separated by spaces.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        reminders_to_delete = []

        for reminder_id in reminder_ids:

            if not (reminder := user_config.get_reminder(reminder_id)):
                raise exceptions.ArgumentError(f'You do not have a reminder with the id `{reminder_id}`.')
            if reminder in reminders_to_delete:
                raise exceptions.ArgumentError(f'You provided the reminder id `{reminder_id}` more than once.')

            reminders_to_delete.append(reminder)

        for reminder in reminders_to_delete:
            await reminder.delete()

        s = 's' if len(reminders_to_delete) > 1 else ''
        await ctx.reply(f'Deleted `{len(reminders_to_delete)}` reminder{s} with id{s} {", ".join(f"`{reminder.id}`" for reminder in reminders_to_delete)}.')

    @reminders.command(name='info')
    async def reminders_info(self, ctx: context.Context, reminder_id: int) -> None:
        """
        Display information about a reminder with the given id.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.ArgumentError('You do not have a reminder with that id.')

        difference = utils.format_difference(reminder.datetime, suppress=[])

        embed = discord.Embed(
                colour=config.MAIN, title=f'Reminder `{reminder.id}`:',
                description=f'''
                [__**{"In " if reminder.done is False else ""}{difference}{" ago" if reminder.done else ""}:**__]({reminder.jump_url})
                `Created:` {utils.format_datetime(reminder.created_at, seconds=True)}
                `Scheduled for:` {utils.format_datetime(reminder.datetime, seconds=True)}
                `Repeat type:` {reminder.repeat_type.name.replace("_", " ").lower().title()}
                `Done:` {reminder.done}
                
                `Content:`
                {reminder.content}
                '''
        )

        await ctx.reply(embed=embed)

    @reminders.command(name='list', aliases=['active'])
    async def reminders_list(self, ctx: context.Context) -> None:
        """
        Display a list of your active reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminders := [reminder for reminder in user_config.reminders.values() if not reminder.done]):
            raise exceptions.ArgumentError('You do not have any active reminders.')

        entries = [
            f'''
            `{reminder.id}`: [__**In {utils.format_difference(reminder.datetime, suppress=[])}**__]({reminder.jump_url})
            `When:` {utils.format_datetime(reminder.datetime, seconds=True)}
            `Content:` {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}
            `Repeat type:` {reminder.repeat_type.name.replace("_", " ").lower().title()}'''
            for reminder in sorted(reminders, key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(entries=entries, per_page=4, title=f'{ctx.author}\'s active reminders:')

    @reminders.command(name='all')
    async def reminders_all(self, ctx: context.Context) -> None:
        """
        Display a list of all your reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.reminders:
            raise exceptions.ArgumentError('You do not have any reminders.')

        entries = [
            f'''
            `{reminder.id}`: [__**{"In " if reminder.done is False else ""}{utils.format_difference(reminder.datetime, suppress=[])}{" ago" if reminder.done else ""}**__]({reminder.jump_url})
            `When:` {utils.format_datetime(reminder.datetime, seconds=True)}
            `Content:` {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}
            `Repeat type:` {reminder.repeat_type.name.replace("_", " ").lower().title()}
            `Done:` {reminder.done}'''
            for reminder in sorted(user_config.reminders.values(), key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(entries=entries, per_page=4, title=f'{ctx.author}\'s reminders:')


def setup(bot: Life) -> None:
    bot.add_cog(Time(bot=bot))
