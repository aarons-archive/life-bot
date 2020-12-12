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
import typing

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
        self.bot.mystbin = mystbin.Client()

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
            info = f'`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

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
    async def on_command_error(self, ctx: context.Context, error) -> typing.Optional[discord.Message]:

        error = getattr(error, 'original', error)

        log.error(f'[COMMANDS] Error while running command. Name: {ctx.command} | Error: {type(error)} | Invoker: {ctx.author} | Channel: {ctx.channel} ({ctx.channel.id}) |'
                  f'{f"Guild: {ctx.guild} ({ctx.guild.id})" if ctx.guild else ""}')

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            message = f'I am missing the following permissions required to run the command `{ctx.command}`.\n{permissions}'
            return await ctx.try_dm(content=message)

        message = None

        if isinstance(error, commands.BadArgument):

            argument = getattr(error, "argument", "None")
            bad_argument_errors = {
                commands.MessageNotFound:               f'A message for the argument `{argument}` was not found.',
                commands.MemberNotFound:                f'A member for the argument `{argument}` was not found.',
                commands.UserNotFound:                  f'A user for the argument `{argument}` was not found.',
                commands.ChannelNotFound:               f'A channel for the argument `{argument}` was not found.',
                commands.RoleNotFound:                  f'A role for the argument `{argument}` was not found.',
                commands.EmojiNotFound:                 f'An emoji for the argument `{argument}` was not found.',
                commands.ChannelNotReadable:            f'I do not have permission to read the channel `{argument}`',
                commands.BadInviteArgument:             f'The invite `{argument}` was not valid or is expired.',
                commands.PartialEmojiConversionFailure: f'The argument `{argument}` did not match the partial emoji format.',
                commands.BadBoolArgument:               f'The argument `{argument}` was not a valid True or False value.',
                commands.BadColourArgument:             f'The argument `{argument}` was not a valid colour type.',
                BadLiteralArgument:                     f'The argument `{argument}` must be one of '
                                                        f'{", ".join([f"`{valid_argument}`" for valid_argument in getattr(error, "valid_arguments", [])])}.',
                commands.BadArgument:                   f'I was unable to convert an argument that you used. Use `{self.bot.config.prefix}help {ctx.command}` for more '
                                                        f'information on what arguments to use.',
            }
            message = bad_argument_errors.get(type(error), 'None')

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_buckets = {
                commands.BucketType.default:  f'for the whole bot.',
                commands.BucketType.user:     f'for you.',
                commands.BucketType.member:   f'for you.',
                commands.BucketType.role:     f'for your role.',
                commands.BucketType.guild:    f'for this server.',
                commands.BucketType.channel:  f'for this channel.',
                commands.BucketType.category: f'for this channel category.'
            }
            message = f'The command `{ctx.command}` is on cooldown {cooldown_buckets.get(error.cooldown.type, "for you.")} You can retry in ' \
                      f'`{self.bot.utils.format_seconds(seconds=error.retry_after, friendly=True)}`'

        elif isinstance(error, commands.MaxConcurrencyReached):
            cooldown_types = {
                commands.BucketType.default:  f'.',
                commands.BucketType.user:     f' per user.',
                commands.BucketType.member:   f' per member.',
                commands.BucketType.role:     f' per role.',
                commands.BucketType.guild:    f' per server.',
                commands.BucketType.channel:  f' per channel.',
                commands.BucketType.category: f' per channel category.',
            }
            message = f'The command `{ctx.command}` is being ran at its maximum of {error.number} time(s){cooldown_types.get(error.per, ".")} Retry a bit later.'

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            message = f'You are missing the following permissions required to run the command `{ctx.command}`.\n{permissions}'

        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You missed the `{error.param.name}` argument. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments to use.'

        elif isinstance(error, commands.BadUnionArgument):
            message = f'I was unable to convert the `{error.param.name}` argument. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments to use.'

        elif isinstance(error, commands.MissingRole):
            message = f'The role `{error.missing_role}` is required to run this command.'

        elif isinstance(error, commands.BotMissingRole):
            message = f'The bot requires the role `{error.missing_role}` to run this command.'

        elif isinstance(error, commands.MissingAnyRole):
            message = f'The roles {", ".join([f"`{role}`" for role in error.missing_roles])} are required to run this command.'

        elif isinstance(error, commands.BotMissingAnyRole):
            message = f'The bot requires the roles {", ".join([f"`{role}`" for role in error.missing_roles])} to run this command.'

        if message:
            return await ctx.send(message)

        error_messages = {
            exceptions.ArgumentError:               f'{error}',
            exceptions.GeneralError:                f'{error}',
            exceptions.ImageError:                  f'{error}',
            exceptions.VoiceError:                  f'{error}',
            NodeNotFound:                           f'There are no lavalink nodes available right now.',

            commands.TooManyArguments:              f'You used too many arguments. Use `{self.bot.config.prefix}help {ctx.command}` for more information on what arguments to use.',

            commands.UnexpectedQuoteError:          f'There was an unexpected quote character in the arguments you passed.',
            commands.InvalidEndOfQuotedStringError: f'There was an unexpected space after a quote character in the arguments you passed.',
            commands.ExpectedClosingQuoteError:     f'There is a missing quote character in the arguments you passed.',

            commands.CheckFailure:                  f'{error}',
            commands.PrivateMessageOnly:            f'The command `{ctx.command}` can only be used in private messages',
            commands.NoPrivateMessage:              f'The command `{ctx.command}` can not be used in private messages.',
            commands.NotOwner:                      f'The command `{ctx.command}` is owner only.',
            commands.NSFWChannelRequired:           f'The command `{ctx.command}` can only be run in a NSFW channel.',

            commands.DisabledCommand:               f'The command `{ctx.command}` has been disabled.',
        }

        message = error_messages.get(type(error), None)
        if message:
            return await ctx.send(message)

        await self.handle_traceback(ctx=ctx, error=error)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        log.info(f'[COMMANDS] Command used. Name: {ctx.command} | Invoker: {ctx.author} | Channel: {ctx.channel} ({ctx.channel.id}) | '
                 f'{f"Guild: {ctx.guild} ({ctx.guild.id})" if ctx.guild else ""}')

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict) -> None:

        event = message.get('t', 'None')
        if event is not None:
            self.bot.socket_stats[event] += 1

    #

    async def handle_traceback(self, *, ctx: context.Context, error) -> None:

        await ctx.send(f'Something went wrong while executing that command. Please use `{self.bot.config.prefix}support` for more help or information.')

        self.bot.error_formatter.theme['_ansi_enabled'] = True
        print(f'\n{"".join(self.bot.error_formatter.format_exception(type(error), error, error.__traceback__)).strip()}\n')

        avatar_url = str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png'))

        info = f'Error in command `{ctx.command}`\n\n' \
               f'{f"`Guild:` {ctx.guild} `{ctx.guild.id}`" if ctx.guild else ""}\n' \
               f'`Channel:` {ctx.channel} `{ctx.channel.id}`\n' \
               f'`Author:` {ctx.author} `{ctx.author.id}`\n' \
               f'`Time:` {self.bot.utils.format_datetime(datetime=pendulum.now(tz="UTC"))}'

        embed = discord.Embed(colour=ctx.colour, description=f'{ctx.message.content}')
        embed.add_field(name='Info:', value=info)

        await self.bot.errors_webhook.send(embed=embed, username=f'{ctx.author}', avatar_url=avatar_url)

        self.bot.error_formatter.theme['_ansi_enabled'] = False
        traceback = "".join(self.bot.error_formatter.format_exception(type(error), error, error.__traceback__)).strip()

        log.error(f'[COMMANDS]\n\n{traceback}\n\n')

        if len(traceback) < 2000:
            traceback = f'```py\n{traceback}\n```'

        else:
            try:
                traceback = await self.bot.mystbin.post(traceback, syntax='python')
            except mystbin.APIError as error:
                log.warning(f'[ERRORS] Error while uploading error traceback to mystbin | Code: {error.status_code} | Message: {error.message}')
                print(f'[ERRORS] Error while uploading error traceback to mystbin | Code: {error.status_code} | Message: {error.message}')

        await self.bot.errors_webhook.send(content=f'{traceback}', username=f'{ctx.author}', avatar_url=avatar_url)


def setup(bot: Life):
    bot.add_cog(Events(bot))
