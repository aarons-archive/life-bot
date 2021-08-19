from typing import Any

from discord.ext import commands, ipc

from core import values
from core.bot import Life


def setup(bot: Life):
    bot.add_cog(IPC(bot=bot))


class IPC(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @ipc.server.route()
    async def basic_information(self, _) -> dict[str, Any]:

        return {
            "users": len(self.bot.users),
            "guilds": len(self.bot.guilds),
            "invite": values.INVITE_LINK,
        }
