import traceback

import discord
from discord.ext import commands

from cogs.utilities import exceptions


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        self.bot.log_channel = self.bot.get_channel(697324016658022441)

        print(f'\n[BOT] The bot is now ready. Logged in as: {self.bot.user} - {self.bot.user.id}\n')
        if self.bot.user.id == 628284183579721747:
            message = f'The bot is now ready. Logged in as: `{self.bot.user}` - `{self.bot.user.id}`'
            await self.bot.log_channel.send(message)

        for guild in self.bot.guilds:
            if guild.id in self.bot.guild_blacklist:
                await guild.leave()
            continue

        await self.bot.change_presence(activity=self.bot.activity)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        await self.bot.log_channel.send(f'Joined a guild: `{guild.name}` - `{guild.id}` - `{guild.owner}`')

        if guild.id in self.bot.guild_blacklist:
            return await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        if guild.id in self.bot.guild_blacklist:
            message = f'Left a blacklisted guild: `{guild.name}` - `{guild.id}` - `{guild.owner}`'
            return await self.bot.log_channel.send(message)

        return await self.bot.log_channel.send(f'Left a guild: `{guild.name}` - `{guild.id}` - `{guild.owner}`')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)
        command = ctx.command
        prefix = self.bot.config.PREFIX
        error_messages = {
            exceptions.BotNotReadyError: f'The bot is not ready yet.',
            exceptions.ArgumentError: f'{error}',
            commands.CheckFailure: f'{error}',
            exceptions.LifePlaylistError: f'{error}',
            exceptions.LifeVoiceError: f'{error}',
            commands.TooManyArguments: f'You used too many parameters for the command `{command}`. '
                                       f'Use `{prefix}help {command}` for more information on what parameters to use.',
            commands.BadArgument: f'I was unable to understand a parameter that you used for the command `{command}`. '
                                  f'Use `{prefix}help {command}` for more information on what parameters to use.',
            commands.BadUnionArgument: f'I was unable to understand a parameter that you used for the command '
                                       f'`{command}`. Use `{prefix}help {command}` for more information on what '
                                       f'parameters to use.',
            commands.NoPrivateMessage: f'The command `{command}` can not be used in private messages.',
            commands.NotOwner: f'The command `{command}` is owner only.',
            commands.NSFWChannelRequired: f'The command `{command}` can only be ran in a NSFW channel.',
            commands.DisabledCommand: f'The command `{command}` has been disabled.',
        }

        error_message = error_messages.get(type(error))

        if isinstance(error, commands.MissingRequiredArgument):
            error_message = f'You missed the `{error.param.name}` parameter for the command `{command}`. ' \
                            f'Use `{prefix}help {command}` for more information on what parameters to use.'

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            error_message = f'You are missing the following permissions required to run the command ' \
                            f'`{command}`.\n{permissions}'

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            error_message = f'I am missing the following permissions required to run the command ' \
                            f'`{command}`.\n{permissions}'

        elif isinstance(error, commands.CommandOnCooldown):
            cooldowns = {
                commands.BucketType.default: f'The command `{command}` is on cooldown for the whole bot.',
                commands.BucketType.user: f'The command `{command}` is on cooldown for you.',
                commands.BucketType.guild: f'The command `{command}` is on cooldown for this server.',
                commands.BucketType.channel: f'The command `{command}` is on cooldown for this channel.',
                commands.BucketType.member: f'The command `{command}` is on cooldown for you.',
                commands.BucketType.category: f'The command `{command}` is on cooldown for this channel category.',
                commands.BucketType.role: f'The command `{command}` is on cooldown for your role.'
            }
            error_message = f'{cooldowns[error.cooldown.type]} You can retry in ' \
                            f'`{self.bot.utils.format_time(error.retry_after, friendly=True)}`'

        elif isinstance(error, commands.MaxConcurrencyReached):
            cooldowns = {
                commands.BucketType.default: f'The command `{command}` is already being ran at its maximum '
                                             f'of {error.number} times per bot.',
                commands.BucketType.user: f'The command `{command}` is already being ran at its maximum '
                                          f'of {error.number} times per user.',
                commands.BucketType.guild: f'The command `{command}` is already being ran at its maximum '
                                           f'of {error.number} times per guild.',
                commands.BucketType.channel: f'The command `{command}` is already being ran at its maximum '
                                             f'of {error.number} times per channel.',
                commands.BucketType.member: f'The command `{command}` is already being ran at its maximum '
                                            f'of {error.number} times per member.',
                commands.BucketType.category: f'The command `{command}` is already being ran at its maximum '
                                              f'of {error.number} times per channel category.',
                commands.BucketType.role: f'The command `{command}` is already being ran at its maximum '
                                          f'of {error.number} times per role.'
            }
            error_message = f'{cooldowns[error.per]} Retry a bit later.'

        elif isinstance(error, commands.CommandNotFound):
            return

        if error_message:
            try:
                return await ctx.send(error_message)
            except discord.Forbidden:
                try:
                    return await ctx.author.send(error_message)
                except discord.Forbidden:
                    return

        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_socket_response(self, msg):

        event = msg.get('t', 'None')
        if event is not None:
            self.bot.socket_stats[event] += 1


def setup(bot):
    bot.add_cog(Events(bot))
