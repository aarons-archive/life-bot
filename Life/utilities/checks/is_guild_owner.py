from discord.ext import commands

from utilities import context


def is_guild_owner():

    def predicate(ctx: context.Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)
