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
import pendulum
from pendulum.datetime import DateTime

import config
from utilities import context, objects, utils

if TYPE_CHECKING:
    from bot import Life

__log__ = logging.getLogger(__name__)


class ReminderManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.scheduler = aioscheduler.Manager(2)

    async def load(self) -> None:

        self.scheduler.start()

        reminders = await self.bot.db.fetch('SELECT * FROM reminders order by datetime')
        for reminder in reminders:

            user_config = await self.bot.user_manager.get_or_create_user_config(user_id=reminder['owner_id'])

            reminder = objects.Reminder(data=dict(reminder))
            if not reminder.done:
                await self.schedule_reminder(reminder=reminder)

            user_config.reminders.append(reminder)

        __log__.info(f'[REMINDER MANAGER] Loaded reminders. [{len(reminders)} reminders]')
        print(f'[REMINDER MANAGER] Loaded reminders. [{len(reminders)} reminders]')

    #

    async def schedule_reminder(self, *, reminder: objects.Reminder) -> None:

        reminder.task = self.scheduler.schedule(self.do_reminder(reminder=reminder), when=reminder.datetime.naive())
        __log__.info(f'[REMINDER MANAGER] Scheduled reminder with id \'{reminder.id}\' for \'{reminder.datetime}\'')

    async def do_reminder(self, *, reminder: objects.Reminder) -> None:

        person = self.bot.get_user(reminder.owner_id)
        if not person:
            __log__.warning(f'[REMINDER MANAGER] Attempted reminder with id \'{reminder.id}\' but user with \'{reminder.owner_id}\' was not found.')
            return

        embed = discord.Embed(colour=discord.Colour(config.COLOUR),
                              description=f'**Reminder:**\n'
                                          f'You said this `{utils.format_difference(datetime=reminder.created_at, suppress=[])}` ago:\n{reminder.content}\n\n'
                                          f'**[Jump to message]({reminder.message_link})**')

        try:
            await person.send(embed=embed)
        except discord.Forbidden:
            __log__.warning(f'[REMINDER MANAGER] Attempted reminder with id \'{reminder.id}\' but user with \'{reminder.owner_id}\' was not able to be DM\'ed.')

    #

    async def get_reminder(self, *, user_id: int, reminder_id: int) -> Optional[objects.Reminder]:

        user_config = self.bot.user_manager.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            return

        reminders = [reminder for reminder in user_config.reminders if reminder.id == reminder_id]
        if not reminders:
            return

        return reminders[0]

    async def create_reminder(self, *, user_id: int, datetime: DateTime, content: str, ctx: context.Context) -> objects.Reminder:

        user_config = self.bot.user_manager.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            user_config = await self.bot.user_manager.create_user_config(user_id=user_id)

        query = 'INSERT INTO reminders (owner_id, created_at, datetime, content, message_link, message_id) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *'
        data = await self.bot.db.fetchrow(query, user_id, pendulum.now(tz='UTC'), datetime, content, ctx.message.jump_url, ctx.message.id)
        __log__.info(f'[REMINDER MANAGER] Created reminder with id \'{data["id"]}\'for user with id \'{user_id}\'')

        reminder = objects.Reminder(data=dict(data))

        if not reminder.done:
            await self.schedule_reminder(reminder=reminder)

        user_config.reminders.append(reminder)
        return reminder

    async def delete_reminder(self, user_id: int, reminder_id: int) -> None:

        user_config = self.bot.user_manager.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            return

        reminders = [reminder for reminder in user_config.reminders if reminder.id == reminder_id]
        if not reminders:
            return

        reminder = reminders[0]
        if reminder.task:
            self.scheduler.cancel(reminder.task)

        await self.bot.db.execute('DELETE FROM reminders WHERE id = $1', reminder.id)
        user_config.reminders.remove(reminder)