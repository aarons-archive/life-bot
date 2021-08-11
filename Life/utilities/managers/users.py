from __future__ import annotations

import io
import logging
import math
import os
import pathlib
import random
from typing import Optional, TYPE_CHECKING

import asyncpg
import discord
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief

from core import colours, emojis
from utilities import exceptions, objects, utils


if TYPE_CHECKING:
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
        ]
    }
}

ARIAL_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/fonts/arial.ttf"))
KABEL_BLACK_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/fonts/kabel_black.otf"))


class UserManager:

    def __init__(self, bot: Life) -> None:
        self.bot: Life = bot

        self.cache: dict[int, objects.UserConfig] = {}

    async def fetch_config(self, user_id: int) -> objects.UserConfig:

        data = await self.bot.db.fetchrow("INSERT INTO users (id) VALUES ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *", user_id)
        user_config = objects.UserConfig(bot=self.bot, data=data)

        await user_config.fetch_notifications()
        await user_config.fetch_todos()
        await user_config.fetch_reminders()
        await user_config.fetch_member_configs()

        self.cache[user_config.id] = user_config

        __log__.debug(f"[USERS] Cached config for '{user_id}'.")
        return user_config

    async def get_config(self, user_id: int) -> objects.UserConfig:

        if (user_config := self.cache.get(user_id)) is not None:
            return user_config

        return await self.fetch_config(user_id)

    async def delete_config(self, user_id: int) -> None:

        await self.bot.db.execute("DELETE FROM users WHERE id = $1", user_id)
        try:
            del self.cache[user_id]
        except KeyError:
            pass

        __log__.info(f"[USERS] Deleted config for '{user_id}'.")

    # Stats

    def timezones(self, *, guild_id: int) -> list[objects.UserConfig]:

        if not (guild := self.bot.get_guild(guild_id)):
            raise ValueError(f"guild with id \"{guild_id}\" was not found.")

        return sorted(
            filter(
                lambda config: (guild.get_member(config.id) if guild else self.bot.get_user(config.id)) is not None and not config.timezone_private and config.timezone is not None,
                self.configs.values()
            ),
            key=lambda config: config.time.offset_hours
        )

    def birthdays(self, *, guild_id: int) -> list[objects.UserConfig]:

        if not (guild := self.bot.get_guild(guild_id)):
            raise ValueError(f"guild with id \"{guild_id}\" was not found.")

        return sorted(
            filter(
                lambda config: (guild.get_member(config.id) if guild else self.bot.get_user(config.id)) is not None and not config.birthday_private and config.birthday is not None,
                self.configs.values()
            ),
            key=lambda config: config.next_birthday
        )

    # Leaderboards

    async def leaderboard(self, *, guild_id: int, page: int, limit: Optional[int] = 10) -> list[asyncpg.Record]:

        data = await self.bot.db.fetch(
            "SELECT user_id, xp, row_number() OVER (ORDER BY xp DESC) AS rank FROM members WHERE guild_id = $1 ORDER BY xp DESC LIMIT $2 OFFSET $3",
            guild_id, limit, (page - 1) * (limit or 0)
        )
        return data

    async def rank(self, *, guild_id: int, user_id: int) -> int:

        data = await self.bot.db.fetchrow(
            "SELECT rank FROM (SELECT user_id, row_number() OVER (ORDER BY xp DESC) AS rank FROM members WHERE members.guild_id = $1) as guild_members WHERE guild_members.user_id = $2",
            guild_id, user_id
        )
        return data["rank"]

    # Images

    async def create_leaderboard(self, *, guild_id: int, page: int) -> io.BytesIO:

        if not (records := await self.leaderboard(guild_id=guild_id, page=page)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There are no users who have gained any xp yet."
            )

        guild = self.bot.get_guild(guild_id)
        data = []

        for record in records:

            member = guild.get_member(record["user_id"])
            avatar_bytes = io.BytesIO(await (member.avatar.replace(format="png", size=256)).read())

            data.append((member, record["xp"], record["rank"], avatar_bytes))

        return await self.bot.loop.run_in_executor(None, self.create_leaderboard_image, data)

    @staticmethod
    def create_leaderboard_image(data: list[tuple[discord.Member, int, int, io.BytesIO]]) -> io.BytesIO:

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

                name_text = f"{member.nick or member.name}"
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

    async def create_level_card(self, *, guild_id: int, user_id: int) -> io.BytesIO:

        guild = self.bot.get_guild(guild_id)
        user_config = await self.get_config(user_id)

        member = guild.get_member(user_id)
        member_config = await user_config.get_member_config(guild_id)
        rank = await self.rank(guild_id=guild_id, user_id=user_id)
        avatar_bytes = io.BytesIO(await (member.avatar.replace(format="png", size=256)).read())

        return await self.bot.loop.run_in_executor(None, self.create_level_card_image, (member, member_config.xp, member_config.needed_xp, member_config.level, rank, avatar_bytes))

    @staticmethod
    def create_level_card_image(data: tuple[discord.Member, int, int, int, int, io.BytesIO]) -> io.BytesIO:

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

    async def create_timecard(self, *, guild_id: int) -> discord.File:

        if not (timezones := self.timezones(guild_id=guild_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their timezone, or everyone has set them to be private."
            )

        timezone_avatars = {}

        for config in timezones:

            avatar_bytes = io.BytesIO(await (self.bot.get_user(config.id).avatar.replace(format="png", size=256)).read())
            timezone = config.time.format("HH:mm (ZZ)")

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

    async def create_birthday_card(self, *, guild_id: int) -> discord.File:

        if not (birthdays := self.birthdays(guild_id=guild_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their birthday, or everyone has set them to be private."
            )

        birthday_avatars = {}

        for config in birthdays:

            avatar_bytes = io.BytesIO(await (self.bot.get_user(config.id).avatar.replace(format="png", size=256)).read())
            birthday_month = config.birthday.format("MMMM")

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
    def create_grid_image(data: dict[str, io.BytesIO]) -> io.BytesIO:

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
