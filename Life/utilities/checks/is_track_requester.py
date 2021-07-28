from discord.ext import commands

from utilities import context


def is_track_requester():

    async def predicate(ctx: context.Context) -> bool:
        return getattr(getattr(getattr(ctx.voice_client, 'current', None), 'requester', None), 'id', None) == ctx.author.id

    return commands.check(predicate)
