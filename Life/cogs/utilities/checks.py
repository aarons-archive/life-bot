from discord.ext import commands


def is_player_playing():
    async def predicate(ctx):
        if not ctx.player.is_playing:
            raise commands.CheckFailure(f'I am not currently playing anything.')
        return True
    return commands.check(predicate)


def is_player_connected():
    async def predicate(ctx):
        if not ctx.player.is_connected:
            raise commands.CheckFailure(f'I am not connected to any voice channels.')
        return True
    return commands.check(predicate)


def is_member_in_channel():
    async def predicate(ctx):
        if not ctx.player.voice_channel == ctx.author.voice.channel:
            raise commands.CheckFailure(f'You are not connected to the same voice channel as me.')
        return True
    return commands.check(predicate)


def is_member_connected():
    async def predicate(ctx):
        if not ctx.author.voice:
            raise commands.CheckFailure(f'You are not connected to any voice channels.')
        return True
    return commands.check(predicate)


def is_krossbot_user():
    async def predicate(ctx):
        guild = ctx.bot.get_guild(491312179476299786)
        role = guild.get_role(548604302768209920)
        if role not in ctx.author.roles:
            raise commands.CheckFailure(f'You must have the role `{role.name}` to use this command.')
        return True
    return commands.check(predicate)


def is_kross_guild():
    async def predicate(ctx):
        guild = ctx.bot.get_guild(491312179476299786)
        if not ctx.guild == guild:
            raise commands.CheckFailure(f'You must be in the guild `{guild.name}` to use this command.')
        return True
    return commands.check(predicate)




