from typing import Literal

from discord.ext import commands

from core import colours, emojis, values
from utilities import context, exceptions


async def global_check(ctx: context.Context) -> Literal[True]:

    user_config = await ctx.bot.user_manager.get_config(ctx.author.id)

    if user_config.blacklisted is True:
        raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"You are blacklisted from using this bot.\n\n"
                            f"*If you would like to appeal this please join my [support server]({values.SUPPORT_LINK}).*"
        )

    current = dict(ctx.channel.permissions_for(ctx.me))
    if not ctx.guild:
        current["read_messages"] = True

    needed = {permission: value for permission, value in values.PERMISSIONS if value is True}

    if missing := [permission for permission, value in needed.items() if current[permission] != value]:
        raise commands.BotMissingPermissions(missing)

    return True
