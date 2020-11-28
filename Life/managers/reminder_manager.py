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

import logging

import aioscheduler
import discord
import pendulum

from utilities import context, objects

log = logging.getLogger(__name__)


class ReminderManager:

    def __init__(self, bot) -> None:
        self.bot = bot

        self.scheduler = aioscheduler.TimedScheduler()

    async def load(self) -> None:

        self.scheduler.start()

        reminders = await self.bot.db.fetch('SELECT * FROM reminders')
        for reminder in reminders:

            user_config = self.bot.user_manager.get_user_config(user_id=reminder['user_id'])
            if isinstance(user_config, objects.DefaultUserConfig):
                user_config = await self.bot.user_manager.create_user_config(user_id=reminder['user_id'])

            reminder = objects.Reminder(data=dict(reminder))

            if not reminder.done:
                await self.schedule_reminder(reminder=reminder)

            user_config.reminders.append(reminder)

        log.info(f'[REMINDER MANAGER] Loaded REMINDERS. [{len(reminders)} reminders]')
        print(f'[REMINDER MANAGER] Loaded REMINDERS. [{len(reminders)} reminders]')

    async def do_reminder(self, *, reminder: objects.Reminder) -> None:

        person = self.bot.get_user(reminder.user_id)
        if not person:
            return

        user_config = self.bot.user_manager.get_user_config(user_id=reminder.user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            user_config = await self.bot.user_manager.create_user_config(user_id=reminder.user_id)

        embed = discord.Embed(colour=user_config.colour,
                              description=f'**[Reminder]({reminder.link}) - {self.bot.utils.format_difference(datetime=reminder.created_at, suppress=[])} ago**\n\n'
                                          f'{reminder.content}\n\n'
                                          f'**Time set:**\n{reminder.created_at.format("dddd Do [of] MMMM YYYY [at] HH:mm:ss A (zz)")}\n'
                                          f'**Time to remind at:**\n{reminder.datetime.format("dddd Do [of] MMMM YYYY [at] HH:mm:ss A (zz)")}')

        if reminder.dm:
            try:
                await person.send(content=f'<@!{reminder.user_id}>', embed=embed)
            except discord.Forbidden:
                return

        else:

            channel = self.bot.get_channel(reminder.channel_id)
            if not channel:
                return

            try:
                await channel.send(content=f'<@!{reminder.user_id}>', embed=embed)
            except discord.Forbidden:
                try:
                    await person.send(content=f'<@!{reminder.user_id}>', embed=embed)
                except discord.Forbidden:
                    return

    async def schedule_reminder(self, *, reminder: objects.Reminder) -> None:

        reminder.task = self.scheduler.schedule(self.do_reminder(reminder=reminder), when=reminder.datetime.naive())
        log.info(f'[REMINDER MANAGER] Scheduled reminder with id \'{reminder.id}\' for \'{reminder.datetime}\'')

    async def create_reminder(self, *, user_id: int, datetime: pendulum.datetime, content: str, ctx: context.Context, dm: bool = False):

        user_config = self.bot.user_manager.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            user_config = await self.bot.user_manager.create_user_config(user_id=user_id)

        query = 'INSERT INTO reminders (user_id, datetime, created_at, content, link, channel_id, message_id, dm) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *'
        data = await self.bot.db.fetchrow(query, user_id, datetime, pendulum.now(tz='UTC'), content, ctx.message.jump_url, ctx.channel.id, ctx.message.id, dm)
        log.info(f'[REMINDER MANAGER] Created reminder with id \'{data["id"]}\'for user with id \'{user_id}\'')

        reminder = objects.Reminder(data=dict(data))

        if not reminder.done:
            await self.schedule_reminder(reminder=reminder)

        user_config.reminders.append(reminder)
        return reminder

    async def delete_reminder(self, user_id: int, reminder_id: int):

        user_config = self.bot.user_manager.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            user_config = await self.bot.user_manager.create_user_config(user_id=user_id)

        reminders = [reminder for reminder in user_config.reminders if reminder.id == reminder_id]
        if not reminders:
            return

        reminder = reminders[0]
        if reminder.task:
            self.scheduler.cancel(reminder.task)

        await self.bot.db.execute('DELETE FROM reminders WHERE id = $1', reminder.id)
        user_config.reminders.remove(reminder)
