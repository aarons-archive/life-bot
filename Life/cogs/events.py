#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#
import logging

import discord
import mystbin
import pendulum
import prettify_exceptions
from discord.ext import commands
from discord.ext.alternatives.literal_converter import BadLiteralArgument

from bot import Life
from cogs.voice.lavalink.exceptions import NodeNotFound
from utilities import context, exceptions

log = logging.getLogger(__name__)


class Events(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.bot.error_formatter = prettify_exceptions.DefaultFormatter()
        self.bot.mystbin = mystbin.MystbinClient()

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        print(f'\n[BOT] The bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}\n')
        log.info(f'Bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:

        log.info(f'Joined a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | Members: {len(guild.members)}')

        time = self.bot.utils.format_datetime(datetime=pendulum.now(tz='UTC'))
        embed = discord.Embed(colour=discord.Colour.gold(), title=f'Joined a guild',
                              description=f'`Name:` {guild.name}\n`ID:` {guild.id}\n`Owner:` {guild.owner}\n`Time:` {time}\n`Members:` {len(guild.members)}')
        embed.set_thumbnail(url=str(guild.icon_url_as(format='gif' if guild.is_icon_animated() else 'png')))
        await self.bot.logging_webhook.send(embed=embed, avatar_url=guild.icon_url_as(format='png'))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        log.info(f'Left a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | Members: {len(guild.members)}')

        time = self.bot.utils.format_datetime(datetime=pendulum.now(tz='UTC'))
        embed = discord.Embed(colour=discord.Colour.gold(), title=f'Left a guild',
                              description=f'`Name:` {guild.name}\n`ID:` {guild.id}\n`Owner:` {guild.owner}\n`Time:` {time}\n`Members:` {len(guild.members)}')
        embed.set_thumbnail(url=str(guild.icon_url_as(format='gif' if guild.is_icon_animated() else 'png')))
        await self.bot.logging_webhook.send(embed=embed, avatar_url=guild.icon_url_as(format='png'))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.id == self.bot.user.id:
            return

        ctx = await self.bot.get_context(message)

        if message.guild is None:

            time = self.bot.utils.format_datetime(datetime=pendulum.now(tz='UTC'))
            info = f'Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

            embed = discord.Embed(colour=ctx.colour, description=f'{message.content}')
            embed.add_field(name='Info:', value=info)
            await self.bot.mentions_dms_webhook.send(embed=embed, username=f'DM from: {ctx.author}',
                                                     avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

        if self.bot.user in message.mentions:

            time = self.bot.utils.format_datetime(datetime=pendulum.now(tz='UTC'))
            info = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

            embed = discord.Embed(colour=ctx.colour, description=f'{message.content}')
            embed.add_field(name='Info:', value=info)
            await self.bot.mentions_dms_webhook.send(embed=embed, username=f'Mentioned by: {ctx.author}',
                                                     avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:

        if before.author.bot:
            return

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: context.Context, error) -> None:

        error = getattr(error, 'original', error)

        log.error(f'[COMMANDS] Error while running command. Name: {ctx.command} | Error: {type(error)} | Invoker: {ctx.author} | Channel: {ctx.channel} ({ctx.channel.id}) |'
                  f'{f"Guild: {ctx.guild} ({ctx.guild.id})" if ctx.guild else ""}')

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_types = {
                commands.BucketType.default: f'for the whole bot.',
                commands.BucketType.user: f'for you.',
                commands.BucketType.member: f'for you.',
                commands.BucketType.role: f'for your role.',
                commands.BucketType.guild: f'for this server.',
                commands.BucketType.channel: f'for this channel.',
                commands.BucketType.category: f'for this channel category.'
            }
            await ctx.send(f'The command `{ctx.command}` is on cooldown {cooldown_types.get(error.cooldown.type, "for you.")} You can retry in '
                           f'`{self.bot.utils.format_seconds(seconds=error.retry_after, friendly=True)}`')
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            cooldowns = {
                commands.BucketType.default: f'.',
                commands.BucketType.user: f' per user.',
                commands.BucketType.member: f' per member.',
                commands.BucketType.role: f' per role.',
                commands.BucketType.guild: f' per server.',
                commands.BucketType.channel: f' per channel.',
                commands.BucketType.category: f' per channel category.',
            }
            await ctx.send(f'The command `{ctx.command}` is being ran at its maximum of {error.number} time(s){cooldowns.get(error.per, ".")} Retry a bit later.')
            return

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            message = f'I am missing the following permissions required to run the command `{ctx.command}`.\n{permissions}'
            try:
                await ctx.send(message)
            except discord.Forbidden:
                try:
                    await ctx.author.send(message)
                except discord.Forbidden:
                    return
            return

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            await ctx.send(f'You are missing the following permissions required to run the command `{ctx.command}`.\n{permissions}')
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'You missed the `{error.param.name}` argument. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments to use.')
            return

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(f'I was unable to convert the `{error.param}` argument. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments '
                           f'to use.')
            return

        elif isinstance(error, commands.MissingRole):
            await ctx.send(f'The role `{error.missing_role}` is required to run this command.')
            return

        elif isinstance(error, commands.BotMissingRole):
            await ctx.send(f'The bot requires the role `{error.missing_role}` to run this command.')
            return

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send(f'The roles {", ".join([f"`{role}`" for role in error.missing_roles])} are required to run this command.')
            return

        elif isinstance(error, commands.BotMissingAnyRole):
            await ctx.send(f'The bot requires the roles {", ".join([f"`{role}`" for role in error.missing_roles])} to run this command.')
            return

        elif isinstance(error, commands.BadArgument):

            if isinstance(error, commands.MessageNotFound):
                await ctx.send(f'A message for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.MemberNotFound):
                await ctx.send(f'A member for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.UserNotFound):
                await ctx.send(f'A user for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotFound):
                await ctx.send(f'A channel for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.RoleNotFound):
                await ctx.send(f'A role for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.EmojiNotFound):
                await ctx.send(f'An emoji for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotReadable):
                await ctx.send(f'I do not have permission to read the channel `{error.argument}`')
            elif isinstance(error, commands.PartialEmojiConversionFailure):
                await ctx.send(f'The argument `{error.argument}` did not match the partial emoji format.')
            elif isinstance(error, commands.BadInviteArgument):
                await ctx.send(f'The invite that matched that argument was not valid or is expired.')
            elif isinstance(error, commands.BadBoolArgument):
                await ctx.send(f'The argument `{error.argument}` was not a valid True/False value.')
            elif isinstance(error, commands.BadColourArgument):
                await ctx.send(f'The argument `{error.argument}` was not a valid colour.')
            elif isinstance(error, BadLiteralArgument):
                await ctx.send(f'The argument `{error.param.name}` must be one of {", ".join([f"`{arg}`" for arg in error.valid_arguments])}.')
            return

        error_messages = {
            exceptions.ArgumentError: f'{error}',
            exceptions.ImageError: f'{error}',
            exceptions.VoiceError: f'{error}',
            NodeNotFound: f'There are no lavalink nodes available right now.',

            commands.TooManyArguments: f'You used too many arguments. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments to use.',

            commands.UnexpectedQuoteError: f'There was an unexpected quote character in the arguments you passed.',
            commands.InvalidEndOfQuotedStringError: f'There was an unexpected space after a quote character in the arguments you passed.',
            commands.ExpectedClosingQuoteError: f'There is a missing quote character in the arguments you passed.',

            commands.BadArgument: f'I was unable to convert an argument that you used. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what '
                                  f'arguments to use.',

            commands.CheckFailure: f'{error}',
            commands.PrivateMessageOnly: f'The command `{ctx.command}` can only be used in private messages',
            commands.NoPrivateMessage: f'The command `{ctx.command}` can not be used in private messages.',
            commands.NotOwner: f'The command `{ctx.command}` is owner only.',
            commands.NSFWChannelRequired: f'The command `{ctx.command}` can only be run in a NSFW channel.',

            commands.DisabledCommand: f'The command `{ctx.command}` has been disabled.',
        }

        error_message = error_messages.get(type(error), None)
        if error_message is not None:
            await ctx.send(error_message)
            return

        await ctx.send(f'Something went wrong while executing that command. Please use `{self.bot.config.prefix}support` for more help or information.')

        self.bot.error_formatter.theme['_ansi_enabled'] = True
        print(f'\n{"".join(self.bot.error_formatter.format_exception(type(error), error, error.__traceback__)).strip()}\n')

        time = self.bot.utils.format_datetime(datetime=pendulum.now(tz='UTC'))
        guild = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n' if ctx.guild else ''
        info = f'Error in command `{ctx.command}`\n\n{guild}`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

        embed = discord.Embed(colour=ctx.colour, description=f'{ctx.message.content}')
        embed.add_field(name='Info:', value=info)

        await self.bot.errors_webhook.send(embed=embed, username=f'{ctx.author}',
                                           avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

        self.bot.error_formatter.theme['_ansi_enabled'] = False
        traceback = "".join(self.bot.error_formatter.format_exception(type(error), error, error.__traceback__)).strip()

        log.error(f'[COMMANDS]\n\n{traceback}\n\n')

        if len(traceback) < 2000:
            traceback = f'```py\n{traceback}\n```'

        else:
            try:
                traceback = await self.bot.mystbin.post(traceback, syntax='python')
            except mystbin.APIError as error:
                log.warning('[ERRORS] Error while uploading error traceback to mystbin | Code: {error.status_code} | Message: {error.message}')
                print(f'[ERRORS] Error while uploading error traceback to mystbin | Code: {error.status_code} | Message: {error.message}')

        await self.bot.errors_webhook.send(content=f'{traceback}', username=f'{ctx.author}',
                                           avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        log.info(f'[COMMANDS] Command used. Name: {ctx.command} | Invoker: {ctx.author} | Channel: {ctx.channel} ({ctx.channel.id}) | '
                 f'{f"Guild: {ctx.guild} ({ctx.guild.id})" if ctx.guild else ""}')

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict) -> None:

        event = message.get('t', 'None')
        if event is not None:
            self.bot.socket_stats[event] += 1


def setup(bot):
    bot.add_cog(Events(bot))
