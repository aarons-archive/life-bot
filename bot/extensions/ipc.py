# Future
from __future__ import annotations

# Standard Library
import re
from typing import Any, Optional

# Packages
from discord.ext import commands
from discord.ext.ipc.server import route

# My stuff
from core import values
from core.bot import Life
from utilities import utils


def setup(bot: Life):
    bot.add_cog(IPC(bot=bot))


class IPC(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @route()
    async def links(self, _) -> dict[str, Any]:
        return {
            "github_link": values.GITHUB_LINK,
            "support_link": values.SUPPORT_LINK,
        }

    @route()
    async def stats(self, _) -> dict[str, Any]:

        return {
            "users": len(self.bot.users),
            "guilds": len(self.bot.guilds),
        }

    #

    @route()
    async def mutual_guild_ids(self, data) -> Optional[list[int]]:

        if not (user := self.bot.get_user(data.user_id)):
            return None

        return [guild.id for guild in user.mutual_guilds]

    @route()
    async def additional_user_info(self, data) -> Optional[dict[str, Any]]:

        if not (user := self.bot.get_user(data.user_id)):
            return None

        badges = utils.badge_emojis(user)
        if badges != "N/A":
            badges = [re.findall(r"\d+", emoji)[0] for emoji in utils.badge_emojis(user).split(" ")]
        else:
            badges = []

        return {
            "created_at": utils.format_datetime(user.created_at),
            "created_ago": utils.format_difference(user.created_at),
            "badges": badges,
        }
