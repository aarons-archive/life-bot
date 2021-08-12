from discord.ext import commands

from utilities import checks, context


def is_mod():

    async def predicate(ctx: context.Context):

        await commands.check_any(
            commands.is_owner(),
            checks.is_guild_owner(),
            checks.has_any_permissions(
                manage_channels=True, manage_roles=True, manage_guild=True, kick_members=True, ban_members=True, administrator=True
            )
        ).predicate(ctx=ctx)

    return commands.check(predicate)
