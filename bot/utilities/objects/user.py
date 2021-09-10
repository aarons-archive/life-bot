# Future
from __future__ import annotations

# Standard Library
import logging
from typing import TYPE_CHECKING, Any

# Packages
import pendulum
from pendulum.tz.timezone import Timezone

# My stuff
from utilities import enums, objects


if TYPE_CHECKING:
    # My stuff
    from core.bot import Life


__log__: logging.Logger = logging.getLogger("utilities.objects.user")


class UserConfig:

    def __init__(self, bot: Life, data: dict[str, Any]) -> None:

        self._bot: Life = bot

        self._id: int = data["id"]
        self._created_at: pendulum.DateTime = pendulum.instance(data["created_at"], tz="UTC")

        self._blacklisted: bool = data["blacklisted"]
        self._blacklisted_reason: str | None = data["blacklisted_reason"]

        self._timezone: Timezone | None = pendulum.timezone(timezone) if (timezone := data["timezone"]) else None
        self._timezone_private: bool = data["timezone_private"]

        self._birthday: pendulum.Date | None = pendulum.Date(birthday.year, birthday.month, birthday.day) if (birthday := data["birthday"]) else None
        self._birthday_private: bool = data["birthday_private"]

        self._notifications: objects.Notifications | None = None
        self._reminders: dict[int, objects.Reminder] = {}
        self._todos: dict[int, objects.Todo] = {}
        self._member_configs: dict[int, objects.MemberConfig] = {}

    def __repr__(self) -> str:
        return f"<UserConfig id={self.id}, blacklisted={self.blacklisted} timezone={self.timezone} birthday={self.birthday}>"

    # Properties

    @property
    def bot(self) -> Life:
        return self._bot

    @property
    def id(self) -> int:
        return self._id

    @property
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def blacklisted(self) -> bool:
        return self._blacklisted

    @property
    def blacklisted_reason(self) -> str | None:
        return self._blacklisted_reason

    @property
    def timezone(self) -> Timezone | None:
        return self._timezone

    @property
    def timezone_private(self) -> bool:
        return self._timezone_private

    @property
    def birthday(self) -> pendulum.Date | None:
        return self._birthday

    @property
    def birthday_private(self) -> bool:
        return self._birthday_private

    #

    @property
    def notifications(self) -> objects.Notifications:
        return self._notifications

    @property
    def reminders(self) -> dict[int, objects.Reminder]:
        return self._reminders

    @property
    def todos(self) -> dict[int, objects.Todo]:
        return self._todos

    @property
    def member_configs(self) -> dict[int, objects.MemberConfig]:
        return self._member_configs

    #

    @property
    def age(self) -> int | None:

        if not self.birthday:
            return None

        now = pendulum.now(tz="UTC")
        date = pendulum.date(year=now.year, month=now.month, day=now.day)

        return (date - self.birthday).in_years()

    @property
    def next_birthday(self) -> pendulum.DateTime | None:

        if not self.birthday or not self.age:
            return None

        now = pendulum.now(tz="UTC")
        date = now.date()

        year = date.year if date < self.birthday.add(years=self.age) else self.birthday.year + self.age + 1
        return now.set(year=year, month=self.birthday.month, day=self.birthday.day, hour=0, minute=0, second=0, microsecond=0)

    @property
    def time(self) -> pendulum.DateTime | None:

        if not self.timezone:
            return None

        return pendulum.now(tz=self.timezone)

    # Config

    async def set_blacklisted(self, blacklisted: bool, *, reason: str | None = None) -> None:

        data = await self.bot.db.fetchrow(
            "UPDATE users SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason",
            blacklisted,
            reason,
            self.id,
        )

        self._blacklisted = data["blacklisted"]
        self._blacklisted_reason = data["blacklisted_reason"]

    async def set_timezone(self, timezone: Timezone | None = None, *, private: bool | None = None) -> None:

        private = self.timezone_private if private is None else private

        data = await self.bot.db.fetchrow(
            "UPDATE users SET timezone = $1, timezone_private = $2 WHERE id = $3 RETURNING timezone, timezone_private",
            timezone.name,
            private,
            self.id,
        )
        self._timezone = pendulum.timezone(tz) if (tz := data.get("timezone")) else None
        self._timezone_private = private

    async def set_birthday(self, birthday: pendulum.Date | None = None, *, private: bool | None = None) -> None:

        private = self.timezone_private if private is None else private

        data = await self.bot.db.fetchrow(
            "UPDATE users SET birthday = $1, birthday_private = $2 WHERE id = $3 RETURNING birthday, birthday_private",
            birthday,
            private,
            self.id,
        )
        self._birthday = pendulum.Date(year=birthday.year, month=birthday.month, day=birthday.day) if (birthday := data.get("birthday")) else None
        self._birthday_private = private

    # Caching

    async def fetch_notifications(self) -> None:

        notification = await self.bot.db.fetchrow(
            "INSERT INTO notifications (user_id) VALUES ($1) ON CONFLICT (user_id) DO UPDATE SET user_id = excluded.user_id RETURNING *",
            self.id,
        )
        self._notifications = objects.Notifications(bot=self.bot, user_config=self, data=notification)

        __log__.debug(f"[USERS] Fetched and cached notification settings for '{self.id}'.")

    async def fetch_todos(self) -> None:

        if not (todos := await self.bot.db.fetch("SELECT * FROM todos WHERE user_id = $1", self.id)):
            return

        for todo_data in todos:
            todo = objects.Todo(bot=self.bot, user_config=self, data=todo_data)
            self._todos[todo.id] = todo

        __log__.debug(f"[USERS] Fetched and cached todos ({len(todos)}) for '{self.id}'.")

    async def fetch_reminders(self) -> None:

        if not (reminders := await self.bot.db.fetch("SELECT * FROM reminders WHERE user_id = $1", self.id)):
            return

        for reminder_data in reminders:

            reminder = objects.Reminder(bot=self.bot, user_config=self, data=reminder_data)
            if not reminder.done:
                reminder.schedule()

            self._reminders[reminder.id] = reminder

        __log__.debug(f"[USERS] Fetched and cached reminders ({len(reminders)}) for '{self.id}'.")

    async def fetch_member_configs(self) -> None:

        if not (member_configs := await self.bot.db.fetch("SELECT * FROM members WHERE user_id = $1", self.id)):
            return

        for member_config_data in member_configs:
            member_config = objects.MemberConfig(user_config=self, data=member_config_data)
            self._member_configs[member_config.guild_id] = member_config

        __log__.debug(f"[USERS] Fetched and cached member configs ({len(member_configs)}) for '{self.id}'.")

    # Todos

    async def create_todo(self, *, content: str, jump_url: str | None = None) -> objects.Todo:

        data = await self.bot.db.fetchrow("INSERT INTO todos (user_id, content, jump_url) VALUES ($1, $2, $3) RETURNING *", self.id, content, jump_url)

        todo = objects.Todo(bot=self.bot, user_config=self, data=data)
        self._todos[todo.id] = todo

        return todo

    def get_todo(self, todo_id: int) -> objects.Todo | None:
        return self.todos.get(todo_id)

    async def delete_todo(self, todo_id: int) -> None:

        if not (todo := self.get_todo(todo_id)):
            return

        await todo.delete()

    # Reminders

    async def create_reminder(
        self,
        *,
        channel_id: int,
        datetime: pendulum.DateTime,
        content: str,
        jump_url: str | None = None,
        repeat_type: enums.ReminderRepeatType = enums.ReminderRepeatType.NEVER,
    ) -> objects.Reminder:

        data = await self.bot.db.fetchrow(
            "INSERT INTO reminders (user_id, channel_id, datetime, content, jump_url, repeat_type) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            self.id,
            channel_id,
            datetime,
            content,
            jump_url,
            repeat_type.value,
        )

        reminder = objects.Reminder(bot=self.bot, user_config=self, data=data)
        self._reminders[reminder.id] = reminder

        if not reminder.done:
            reminder.schedule()

        return reminder

    def get_reminder(self, reminder_id: int) -> objects.Reminder | None:
        return self.reminders.get(reminder_id)

    async def delete_reminder(self, reminder_id: int) -> None:

        if not (reminder := self.get_reminder(reminder_id)):
            return

        await reminder.delete()

    # Member configs

    async def fetch_member_config(self, guild_id: int) -> objects.MemberConfig:

        data = await self.bot.db.fetchrow(
            "INSERT INTO members (user_id, guild_id) VALUES ($1, $2) ON CONFLICT (user_id, guild_id) DO UPDATE SET user_id = excluded.user_id RETURNING *",
            self.id,
            guild_id,
        )
        member_config = objects.MemberConfig(bot=self.bot, user_config=self, data=data)

        self._member_configs[member_config.guild_id] = member_config

        __log__.debug(f"[USERS] Cached member config for user '{self.id}' in guild '{guild_id}'.")
        return member_config

    async def get_member_config(self, guild_id: int) -> objects.MemberConfig:

        if (member_config := self._member_configs.get(guild_id)) is not None:
            return member_config

        return await self.fetch_member_config(guild_id)

    async def delete_config(self, guild_id: int) -> None:

        await self.bot.db.execute("DELETE FROM members WHERE user_id = $1 AND guild_id = $2", self.id, guild_id)
        try:
            del self._member_configs[guild_id]
        except KeyError:
            pass

        __log__.info(f"[USERS] Deleted member config for '{self.id}' in guild '{guild_id}'.")
