# Future
from __future__ import annotations

# Standard Library
import io
import logging
import math
import os
import pathlib
import random
from typing import TYPE_CHECKING

# Packages
import asyncpg
import discord
import pendulum
from colorthief import ColorThief
from pendulum.tz.timezone import Timezone
from PIL import Image, ImageDraw, ImageFont

# My stuff
from core import colours, emojis
from utilities import exceptions, objects, utils


if TYPE_CHECKING:
    # My stuff
    from core.bot import Life

__log__: logging.Logger = logging.getLogger("utilities.managers.users")

IMAGES = {
    "SAI": {
        "level_cards": [
            pathlib.Path("./resources/SAI/level_cards/1.png"),
            pathlib.Path("./resources/SAI/level_cards/2.png"),
            pathlib.Path("./resources/SAI/level_cards/3.png"),
            pathlib.Path("./resources/SAI/level_cards/4.png"),
            pathlib.Path("./resources/SAI/level_cards/5.png"),
            pathlib.Path("./resources/SAI/level_cards/6.png"),
            pathlib.Path("./resources/SAI/level_cards/7.png"),
            pathlib.Path("./resources/SAI/level_cards/8.png"),
            pathlib.Path("./resources/SAI/level_cards/9.png"),
        ],
        "leaderboard": [
            pathlib.Path("./resources/SAI/leaderboard/1.png"),
            pathlib.Path("./resources/SAI/leaderboard/2.png"),
            pathlib.Path("./resources/SAI/leaderboard/3.png"),
            pathlib.Path("./resources/SAI/leaderboard/4.png"),
            pathlib.Path("./resources/SAI/leaderboard/5.png"),
            pathlib.Path("./resources/SAI/leaderboard/6.png"),
        ],
    }
}

ARIAL_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/fonts/arial.ttf"))
KABEL_BLACK_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/fonts/kabel_black.otf"))


class UserManager:

    def __init__(self, bot: Life) -> None:
        self.bot: Life = bot

        self.cache: dict[int, objects.UserConfig] = {}

    async def fetch_config(
        self,
        user_id: int,
        /
    ) -> objects.UserConfig:

        data = await self.bot.db.fetchrow("INSERT INTO users (id) VALUES ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *", user_id)
        user_config = objects.UserConfig(bot=self.bot, data=data)

        await user_config.fetch_notifications()
        await user_config.fetch_todos()
        await user_config.fetch_reminders()
        await user_config.fetch_member_configs()

        self.cache[user_config.id] = user_config

        __log__.debug(f"[USERS] Cached config for '{user_id}'.")
        return user_config

    async def get_config(
        self,
        user_id: int,
        /
    ) -> objects.UserConfig:

        if (user_config := self.cache.get(user_id)) is not None:
            return user_config

        return await self.fetch_config(user_id)

    async def delete_config(
        self,
        user_id: int,
        /
    ) -> None:

        await self.bot.db.execute("DELETE FROM users WHERE id = $1", user_id)
        try:
            del self.cache[user_id]
        except KeyError:
            pass

        __log__.info(f"[USERS] Deleted config for '{user_id}'.")

    #

    async def timezones(
        self,
        *,
        guild_id: int
    ) -> list[tuple[discord.Member, Timezone, pendulum.DateTime]]:

        records = await self.bot.db.fetch("SELECT id, timezone FROM users WHERE NOT timezone IS NULL and timezone_private IS FALSE")

        guild = self.bot.get_guild(guild_id)
        data = []

        for record in records:

            if not (member := guild.get_member(record["id"])):
                continue

            timezone = pendulum.timezone(record["timezone"])

            data.append((member, timezone, pendulum.now(tz=timezone)))

        return sorted(data, key=lambda item: item[2].offset_hours)

    async def birthdays(
        self,
        *,
        guild_id: int
    ) -> list[tuple[discord.Member, pendulum.Date, int, pendulum.DateTime]]:

        records = await self.bot.db.fetch("SELECT id, birthday FROM users WHERE NOT birthday IS NULL and birthday_private IS FALSE ORDER BY birthday DESC")

        guild = self.bot.get_guild(guild_id)
        data = []

        for record in records:

            if not (member := guild.get_member(record["id"])):
                continue

            birthday_date = record["birthday"]
            birthday = pendulum.Date(birthday_date.year, birthday_date.month, birthday_date.day)

            now_age = pendulum.now(tz="UTC")
            age = (pendulum.date(year=now_age.year, month=now_age.month, day=now_age.day) - birthday).in_years()

            next_birthday_now = pendulum.now(tz="UTC")
            next_birthday_date = next_birthday_now.date()

            next_birthday_year = next_birthday_date.year if next_birthday_date < birthday.add(years=age) else birthday.year + age + 1
            next_birthday = next_birthday_now.set(year=next_birthday_year, month=birthday.month, day=birthday.day, hour=0, minute=0, second=0, microsecond=0)

            data.append((member, birthday, age, next_birthday))

        return sorted(data, key=lambda item: item[3])

    async def leaderboard(
        self,
        *,
        guild_id: int,
        page: int,
        limit: int | None = 10
    ) -> list[asyncpg.Record]:

        data = await self.bot.db.fetch(
            "SELECT user_id, xp, row_number() OVER (ORDER BY xp DESC) AS rank FROM members WHERE guild_id = $1 ORDER BY xp DESC LIMIT $2 OFFSET $3",
            guild_id,
            limit,
            (page - 1) * (limit or 0),
        )
        return data

    async def rank(
        self,
        *,
        user_id: int,
        guild_id: int,
    ) -> int:

        data = await self.bot.db.fetchrow(
            "SELECT rank "
            "FROM (SELECT user_id, row_number() OVER (ORDER BY xp DESC) AS rank FROM members WHERE members.guild_id = $1) as guild_members "
            "WHERE guild_members.user_id = $2",
            guild_id,
            user_id,
        )
        return data["rank"]

    #

    async def create_leaderboard(
        self,
        *,
        guild_id: int,
        page: int
    ) -> io.BytesIO:

        if not (records := await self.leaderboard(guild_id=guild_id, page=page)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There are no users who have gained any xp yet."
            )

        guild = self.bot.get_guild(guild_id)
        data = []

        for record in records:

            if not (person := guild.get_member(record["user_id"])):
                person = await self.bot.fetch_user(record["user_id"])

            data.append(
                (
                    person,
                    record["xp"],
                    record["rank"],
                    io.BytesIO(await (person.avatar.replace(format="png", size=256)).read()),
                )
            )

        return await self.bot.loop.run_in_executor(None, self.create_leaderboard_image, data)

    @staticmethod
    def create_leaderboard_image(
        data: list[tuple[discord.Member | discord.User, int, int, io.BytesIO]]
    ) -> io.BytesIO:

        with Image.open(fp=random.choice(IMAGES["SAI"]["leaderboard"])) as image:

            draw = ImageDraw.Draw(im=image)
            y = 100

            # Title

            title_text = "XP Leaderboard:"
            title_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=93)
            draw.text(xy=(10, 10 - title_font.getoffset(text=title_text)[1]), text=title_text, font=title_font, fill="#1F1E1C")

            # Actual content

            for member, xp, rank, avatar_bytes in data:

                # Avatar

                with Image.open(fp=avatar_bytes) as avatar:
                    avatar = avatar.resize(size=(80, 80), resample=Image.LANCZOS)
                    image.paste(im=avatar, box=(10, y), mask=avatar.convert("RGBA"))

                avatar_bytes.close()

                # Username

                name_text = f"{getattr(member, 'nick', None) or member.name}"
                name_fontsize = 45
                name_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=name_fontsize)

                while draw.textsize(text=name_text, font=name_font) > (600, 30):
                    name_fontsize -= 1
                    name_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=name_fontsize)

                draw.text(xy=(100, y - name_font.getoffset(text=name_text)[1]), text=name_text, font=name_font, fill="#1F1E1C")

                #

                y += 45

                # Rank

                rank_text = f"#{rank}"
                rank_fontsize = 40
                rank_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=rank_fontsize)

                while draw.textsize(text=rank_text, font=rank_font) > (600, 30):
                    rank_fontsize -= 1
                    rank_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=rank_fontsize)

                draw.text(xy=(100, y - rank_font.getoffset(text=rank_text)[1]), text=rank_text, font=rank_font, fill="#1F1E1C")

                # Xp

                level = utils.level(xp)
                needed_xp = utils.needed_xp(level, xp)

                xp_text = f"XP: {xp}/{xp + needed_xp}"
                xp_fontsize = 40
                xp_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=xp_fontsize)

                while draw.textsize(text=xp_text, font=xp_font) > (320, 30):
                    xp_fontsize -= 1
                    xp_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=xp_fontsize)

                draw.text(xy=(220, y - xp_font.getoffset(text=xp_text)[1]), text=xp_text, font=xp_font, fill="#1F1E1C")

                # Level

                level_text = f"Level: {level}"
                level_fontsize = 40
                level_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=level_fontsize)

                while draw.textsize(text=level_text, font=level_font) > (150, 30):
                    level_fontsize -= 1
                    level_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=level_fontsize)

                draw.text(xy=(545, y - level_font.getoffset(text=xp_text)[1]), text=level_text, font=level_font, fill="#1F1E1C")

                #

                y += 45

            buffer = io.BytesIO()
            image.save(buffer, "png")

        buffer.seek(0)
        return buffer

    #

    async def create_level_card(
        self,
        *,
        user_id: int,
        guild_id: int
    ) -> io.BytesIO:

        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)

        user_config = await self.get_config(user_id)
        member_config = await user_config.get_member_config(guild_id)

        rank = await self.rank(user_id=user_id, guild_id=guild_id)
        avatar_bytes = io.BytesIO(await (member.avatar.replace(format="png", size=256)).read())

        return await self.bot.loop.run_in_executor(
            None,
            self.create_level_card_image,
            (member, member_config.xp, member_config.needed_xp, member_config.level, rank, avatar_bytes),
        )

    @staticmethod
    def create_level_card_image(
        data: tuple[discord.Member, int, int, int, int, io.BytesIO]
    ) -> io.BytesIO:

        member, xp, needed_xp, level, rank, avatar_bytes = data

        with Image.open(fp=random.choice(IMAGES["SAI"]["level_cards"])) as image:

            draw = ImageDraw.Draw(im=image)

            with Image.open(fp=avatar_bytes) as avatar:

                avatar = avatar.resize(size=(256, 256), resample=Image.LANCZOS) if avatar.size != (256, 256) else avatar
                image.paste(im=avatar, box=(22, 22), mask=avatar.convert("RGBA"))

                colour = ColorThief(file=avatar_bytes).get_color(quality=1)

            # Username

            name_text = member.nick or member.name
            name_fontsize = 56
            name_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=name_fontsize)

            while draw.textsize(text=name_text, font=name_font) > (690, 45):
                name_fontsize -= 1
                name_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=name_fontsize)

            draw.text(xy=(300, 22 - name_font.getoffset(text=name_text)[1]), text=name_text, font=name_font, fill=colour)

            # Level

            level_text = f"Level: {level}"
            level_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=40)

            draw.text(xy=(300, 72 - level_font.getoffset(text=level_text)[1]), text=level_text, font=level_font, fill="#1F1E1C")

            # XP

            xp_text = f"XP: {xp} / {xp + needed_xp}"
            xp_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=40)

            draw.text(xy=(300, 112 - xp_font.getoffset(text=xp_text)[1]), text=xp_text, font=xp_font, fill="#1F1E1C")

            # XP BAR

            bar_len = 678
            outline = utils.darken_colour(*colour, factor=0.2)

            draw.rounded_rectangle(xy=((300, 152), (300 + bar_len, 192)), radius=10, outline=outline, fill="#1F1E1C", width=5)

            if xp > 0:
                filled_len = int(round(bar_len * xp / float(xp + needed_xp)))
                draw.rounded_rectangle(xy=((300, 152), (300 + filled_len, 192)), radius=10, outline=outline, fill=colour, width=5)

            # Rank

            rank_text = f"#{rank}"
            rank_font = ImageFont.truetype(font=KABEL_BLACK_FONT, size=110)

            draw.text(xy=(300, 202 - rank_font.getoffset(text=rank_text)[1]), text=rank_text, font=rank_font, fill="#1F1E1C")

            #

            buffer = io.BytesIO()
            image.save(buffer, "png")

        buffer.seek(0)
        return buffer

    #

    async def create_timecard(
        self,
        *,
        guild_id: int
    ) -> discord.File:

        if not (timezones := await self.timezones(guild_id=guild_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their timezone, or everyone has set them to be private.",
            )

        timezone_avatars = {}

        for member, timezone, time in timezones:

            avatar_bytes = io.BytesIO(await (member.avatar.replace(format="png", size=256)).read())
            timezone = time.format("HH:mm (ZZ)")

            if users := timezone_avatars.get(timezone, []):
                if len(users) > 36:
                    break
                timezone_avatars[timezone].append(avatar_bytes)
            else:
                timezone_avatars[timezone] = [avatar_bytes]

        buffer = await self.bot.loop.run_in_executor(None, self.create_grid_image, timezone_avatars)
        file = discord.File(fp=buffer, filename="timecard.png")

        buffer.close()
        for avatar_bytes in timezone_avatars.values():
            [buffer.close() for buffer in avatar_bytes]

        return file

    async def create_birthday_card(
        self,
        *,
        guild_id: int
    ) -> discord.File:

        if not (birthdays := await self.birthdays(guild_id=guild_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their birthday, or everyone has set them to be private.",
            )

        birthday_avatars = {}

        for member, birthday, _, _ in birthdays:

            avatar_bytes = io.BytesIO(await (member.avatar.replace(format="png", size=256)).read())
            birthday_month = birthday.format("MMMM")

            if users := birthday_avatars.get(birthday_month, []):
                if len(users) > 36:
                    break
                birthday_avatars[birthday_month].append(avatar_bytes)
            else:
                birthday_avatars[birthday_month] = [avatar_bytes]

        buffer = await self.bot.loop.run_in_executor(None, self.create_grid_image, birthday_avatars)
        file = discord.File(fp=buffer, filename="birthday.png")

        buffer.close()
        for avatar_bytes in birthday_avatars.values():
            [buffer.close() for buffer in avatar_bytes]

        return file

    @staticmethod
    def create_grid_image(
        data: dict[str, io.BytesIO]
    ) -> io.BytesIO:

        width_x, height_y = ((1600 * min(len(data), 5)) + 100), ((1800 * math.ceil(len(data) / 5)) + 100)

        with Image.new(mode="RGBA", size=(width_x, height_y), color=colours.MAIN.to_rgb()) as image:

            draw = ImageDraw.Draw(im=image)
            font = ImageFont.truetype(font=ARIAL_FONT, size=120)

            x, y = 100, 100

            for timezone, avatars in data.items():

                draw.text(xy=(x, y), text=timezone, font=font, fill="#1B1A1C")
                user_x, user_y = x, y + 200

                for avatar_bytes in avatars:

                    with Image.open(fp=avatar_bytes) as avatar:
                        avatar = avatar.resize(size=(250, 250), resample=Image.LANCZOS)
                        image.paste(im=avatar, box=(user_x, user_y), mask=avatar.convert(mode="RGBA"))

                    if user_x < x + 1200:
                        user_x += 250
                    else:
                        user_y += 250
                        user_x = x

                if x > 6400:
                    y += 1800
                    x = 100
                else:
                    x += 1600

            buffer = io.BytesIO()
            image.save(fp=buffer, format="png")

        buffer.seek(0)
        return buffer
