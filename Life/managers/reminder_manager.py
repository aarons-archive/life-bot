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

from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING

import aioscheduler
import discord
from pendulum.datetime import DateTime

from utilities import enums, exceptions, objects, utils

if TYPE_CHECKING:
    from bot import Life

__log__ = logging.getLogger(__name__)


class ReminderManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.scheduler = aioscheduler.Manager(2)

        self.REPEAT_TYPE_TIMES = {
            1: lambda dt: dt.add(minutes=30),
            2: lambda dt: dt.add(hours=1),
            3: lambda dt: dt.add(hours=2),

            4: lambda dt: dt.add(hours=12),
            5: lambda dt: dt.add(days=1),
            6: lambda dt: dt.add(days=2),

            7: lambda dt: dt.add(days=7),
            8: lambda dt: dt.add(days=14),

            9: lambda dt: dt.add(weeks=2),
            10: lambda dt: dt.add(months=1),
            11: lambda dt: dt.add(months=2),

            12: lambda dt: dt.add(months=6),
            13: lambda dt: dt.add(years=1),
            14: lambda dt: dt.add(years=2)
        }

    async def load(self) -> None:

        self.scheduler.start()

        reminders = await self.bot.db.fetch('SELECT * FROM reminders order by datetime')
        for reminder_data in reminders:

            reminder = objects.Reminder(data=reminder_data)
            if not reminder.done:
                await self.schedule_reminder(reminder)

            user_config = await self.bot.user_manager.get_or_create_config(reminder.user_id)
            user_config.reminders[reminder.id] = reminder

        __log__.info(f'[REMINDER MANAGER] Loaded reminders. [{len(reminders)} reminders]')
        print(f'[REMINDER MANAGER] Loaded reminders. [{len(reminders)} reminders]')

    #

    async def schedule_reminder(self, reminder: objects.Reminder) -> None:

        reminder.task = self.scheduler.schedule(self.do_reminder(reminder), when=reminder.datetime.naive())
        __log__.info(f'[REMINDER MANAGER] Scheduled reminder with id \'{reminder.id}\' for \'{reminder.datetime}\'')

    async def do_reminder(self, reminder: objects.Reminder) -> None:

        user = self.bot.get_user(reminder.user_id)
        channel = self.bot.get_channel(reminder.channel_id)
        user_config = self.bot.user_manager.get_config(reminder.user_id)

        embed = discord.Embed(
                colour=user_config.colour,
                description=f'**Reminder:**\n'
                            f'You said this `{utils.format_difference(datetime=reminder.created_at, suppress=[])}` ago:\n'
                            f'{reminder.content}\n\n'
                            f'**[Jump to message]({reminder.jump_url})**'
        )

        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, AttributeError):
            try:
                await user.send(embed=embed)
            except (discord.Forbidden, AttributeError):
                __log__.warning(f'[REMINDER MANAGER] Attempted reminder with id \'{reminder.id}\' but channel or user did not exist.')

        await self.bot.db.execute('UPDATE reminders SET notified = true WHERE id = $1', reminder.id)
        reminder.notified = True

        if reminder.repeat_type != enums.ReminderRepeatType.NEVER:
            await self.create_reminder(
                    reminder.user_id, channel_id=reminder.channel_id, datetime= self.REPEAT_TYPE_TIMES[reminder.repeat_type](reminder.datetime), content=reminder.content,
                    jump_url=reminder.jump_url, repeat_type=reminder.repeat_type
            )

    #

    async def get_reminder(self, user_id: int, *, reminder_id: int) -> Optional[objects.Reminder]:

        user_config = await self.bot.user_manager.get_or_create_config(user_id)
        return user_config.reminders.get(reminder_id)

    async def create_reminder(
            self, user_id: int, *, channel_id: int, datetime: DateTime, content: str, jump_url: str = None, repeat_type: enums.ReminderRepeatType = enums.ReminderRepeatType.NEVER
    ) -> objects.Reminder:

        user_config = await self.bot.user_manager.get_or_create_config(user_id)

        query = 'INSERT INTO reminders (user_id, channel_id, datetime, content, jump_url, repeat_type) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *'
        data = await self.bot.db.fetchrow(query, user_id, channel_id, datetime, content, jump_url, repeat_type.value)

        reminder = objects.Reminder(data=data)
        user_config.reminders[reminder.id] = reminder

        if not reminder.done:
            await self.schedule_reminder(reminder)

        __log__.info(f'[REMINDER MANAGER] Created reminder with id \'{reminder.id}\'for user with id \'{reminder.user_id}\'.')
        return reminder

    async def delete_reminder(self, user_id: int, *, reminder_id: int) -> None:

        user_config = await self.bot.user_manager.get_or_create_config(user_id)

        if not (reminder := await self.get_reminder(user_id, reminder_id=reminder_id)):
            raise exceptions.NotFound(f'You do not have a reminder with that id.')

        if reminder.task:
            self.scheduler.cancel(reminder.task)

        await self.bot.db.execute('DELETE FROM reminders WHERE id = $1', reminder.id)
        del user_config.reminders[reminder_id]

    async def change_reminder_content(self, user_id: int, *, reminder_id: int, content: str, jump_url: str = None) -> None:

        if not (reminder := await self.get_reminder(user_id, reminder_id=reminder_id)):
            raise exceptions.NotFound(f'You do not have a reminder with that id.')

        await self.bot.db.execute('UPDATE reminders SET content = $1, jump_url = $2 WHERE id = $3', content, jump_url, reminder.id)
        reminder.content = content
        reminder.jump_url = jump_url if jump_url else reminder.jump_url

    async def change_reminder_repeat_type(self, user_id: int, *, reminder_id: int, repeat_type: enums.ReminderRepeatType) -> None:

        if not (reminder := await self.get_reminder(user_id, reminder_id=reminder_id)):
            raise exceptions.NotFound(f'You do not have a reminder with that id.')

        await self.bot.db.execute('UPDATE reminders SET repeat_type = $1 WHERE id = $2', repeat_type.value, reminder.id)
        reminder.repeat_type = repeat_type
