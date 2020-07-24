from discord.ext import commands


def has_guild_permissions(**perms):
    def predicate(ctx):

        if ctx.author.id in ctx.bot.config.owner_ids:
            return True

        permissions = ctx.author.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if missing:
            raise commands.MissingPermissions(missing)

        return True

    return commands.check(predicate)


def bot_has_guild_permissions(**perms):
    def predicate(ctx):

        permissions = ctx.me.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if missing:
            raise commands.MissingPermissions(missing)

        return True

    return commands.check(predicate)
