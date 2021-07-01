"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import textwrap

import discord
from discord.ext import commands

import colours
from bot import Life
from utilities import context, converters, exceptions, utils


class Reminders(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    #

    @commands.group(name='remind', aliases=['reminder', 'reminders'], invoke_without_command=True)
    async def remind(self, ctx: context.Context, *, when: converters.DatetimeConverter) -> None:
        """
        Set a reminder.

        `when`: The subject you want to be reminded about, should include some form of time such as `tomorrow`, `10am`, or `3 hours`.

        **Usage:**
        `l-remind in 3 hours do that thing you talked about doing.`
        """

        entries = {index: (phrase, datetime) for index, (phrase, datetime) in enumerate(when[1].items())}

        choice = await ctx.choice(
                entries=[f'{index + 1}: **{phrase}**\n`{utils.format_datetime(datetime)}`' for index, (phrase, datetime) in entries.items()],
                per_page=5,
                splitter='\n\n',
                title='Multiple dates/times where detected in your reminder:',
                header='Choose the option that best matches your intended reminder time.\n\n'
        )
        _, datetime = entries[choice]

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        reminder = await user_config.create_reminder(
                channel_id=ctx.channel.id,
                datetime=datetime,
                content=await utils.safe_content(self.bot.mystbin, when[0], max_characters=1500),
                jump_url=ctx.message.jump_url
        )

        embed = discord.Embed(
                colour=colours.GREEN,
                description=f'Reminder with id **{reminder.id}** created for **{discord.utils.format_dt(reminder.datetime, "F")}**, '
                            f'which is in **{utils.format_difference(reminder.datetime)}**.'
        )
        await ctx.reply(embed=embed)


    @remind.command(name='edit')
    async def remind_edit(self, ctx: context.Context, reminder_id: int, *, content: str) -> None:
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

    @remind.group(name='repeat')
    async def remind_repeat(self, ctx: context.Context, reminder_id: int, *, repeat_type: converters.ReminderRepeatTypeConverter) -> None:
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

    @remind.command(name='delete')
    async def remind_delete(self, ctx: context.Context, reminder_ids: commands.Greedy[int]) -> None:
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

    @remind.command(name='info')
    async def remind_info(self, ctx: context.Context, reminder_id: int) -> None:
        """
        Display information about a reminder with the given id.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.ArgumentError('You do not have a reminder with that id.')

        difference = utils.format_difference(reminder.datetime, suppress=[])

        embed = discord.Embed(
                colour=colours.MAIN, title=f'Reminder `{reminder.id}`:',
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

    @remind.command(name='list', aliases=['active'])
    async def remind_list(self, ctx: context.Context) -> None:
        """
        Display a list of your active reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminders := [reminder for reminder in user_config.reminders.values() if not reminder.done]):
            raise exceptions.ArgumentError('You do not have any active reminders.')

        entries = [
            textwrap.dedent(
                    f'''
                `{reminder.id}`: [__**In {utils.format_difference(reminder.datetime, suppress=[])}**__]({reminder.jump_url})
                `When:` {utils.format_datetime(reminder.datetime, seconds=True)}
                `Content:` {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}
                `Repeat type:` {reminder.repeat_type.name.replace("_", " ").lower().title()}
                '''
            )
            for reminder in sorted(reminders, key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(entries=entries, per_page=4, title=f'{ctx.author}\'s active reminders:')

    @remind.command(name='all')
    async def remind_all(self, ctx: context.Context) -> None:
        """
        Display a list of all your reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.reminders:
            raise exceptions.ArgumentError('You do not have any reminders.')

        entries = [
            textwrap.dedent(
                    f'''
                `{reminder.id}`: [__**{"In " if reminder.done is False else ""}{utils.format_difference(reminder.datetime, suppress=[])}{" ago" if reminder.done else ""}**__]({reminder.jump_url})
                `When:` {utils.format_datetime(reminder.datetime, seconds=True)}
                `Content:` {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}
                `Repeat type:` {reminder.repeat_type.name.replace("_", " ").lower().title()}
                `Done:` {reminder.done}
                '''
            )
            for reminder in sorted(user_config.reminders.values(), key=lambda reminder: reminder.datetime)

        ]

        await ctx.paginate_embed(entries=entries, per_page=4, title=f'{ctx.author}\'s reminders:')

    #


def setup(bot: Life) -> None:
    bot.add_cog(Reminders(bot=bot))
