"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime

import discord
import prettify_exceptions
from discord.ext import commands

from bot import Life
from cogs.voice.lavalink.exceptions import NodeNotFound
from utilities import context, exceptions


class Events(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        print(f'\n[BOT] The bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}\n')
        self.bot.log.info(f'Bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}')

        for guild in self.bot.guilds:
            if guild.id in self.bot.guild_blacklist:
                await guild.leave()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:

        self.bot.log.info(f'Joined a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | Members: {len(guild.members)}')

        time = self.bot.utils.format_datetime(time=datetime.now())
        embed = discord.Embed(colour=discord.Colour.gold(), title=f'Joined a guild',
                              description=f'`Name:` {guild.name}\n`ID:` {guild.id}\n`Owner:` {guild.owner}\n`Time:` {time}\n`Members:` {len(guild.members)}')
        embed.set_thumbnail(url=str(guild.icon_url_as(format='gif' if guild.is_icon_animated() else 'png')))
        await self.bot.logging_webhook.send(embed=embed, avatar_url=guild.icon_url_as(format='png'))

        if guild.id in self.bot.guild_blacklist.keys():
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        self.bot.log.info(f'Left a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | Members: {len(guild.members)}')

        time = self.bot.utils.format_datetime(time=datetime.now())
        embed = discord.Embed(colour=discord.Colour.gold(), title=f'Left a {"blacklisted " if guild.id in self.bot.guild_blacklist.keys() else ""}guild',
                              description=f'`Name:` {guild.name}\n`ID:` {guild.id}\n`Owner:` {guild.owner}\n`Time:` {time}\n`Members:` {len(guild.members)}')
        embed.set_thumbnail(url=str(guild.icon_url_as(format='gif' if guild.is_icon_animated() else 'png')))
        await self.bot.logging_webhook.send(embed=embed, avatar_url=guild.icon_url_as(format='png'))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.id == self.bot.user.id:
            return

        ctx = await self.bot.get_context(message)

        if message.guild is None:

            time = self.bot.utils.format_datetime(time=datetime.now())
            guild = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n' if ctx.guild else ''
            info = f'{guild}`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

            embed = discord.Embed(colour=ctx.colour, description=f'{message.content}')
            embed.add_field(name='Info:', value=info)
            await self.bot.mentions_dms_webhook.send(embed=embed, username=f'DM from: {ctx.author}',
                                                     avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

        if self.bot.user in message.mentions:

            time = self.bot.utils.format_datetime(time=datetime.now())
            guild = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n' if ctx.guild else ''
            info = f'{guild}`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

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

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.CommandOnCooldown):

            cooldowns = {
                commands.BucketType.default: f'for the whole bot.',
                commands.BucketType.user: f'for you.',
                commands.BucketType.guild: f'for this server.',
                commands.BucketType.channel: f'for this channel.',
                commands.BucketType.member: f'cooldown for you.',
                commands.BucketType.category: f'for this channel category.',
                commands.BucketType.role: f'for your role.'
            }
            await ctx.send(f'The command `{ctx.command}` is on cooldown {cooldowns[error.cooldown.type]} You can retry in '
                           f'`{self.bot.utils.format_seconds(seconds=error.retry_after, friendly=True)}`')
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            cooldowns = {
                commands.BucketType.default: f'.',
                commands.BucketType.user: f' per user.',
                commands.BucketType.guild: f' per server.',
                commands.BucketType.channel: f' per channel.',
                commands.BucketType.member: f' per member.',
                commands.BucketType.category: f' per channel category.',
                commands.BucketType.role: f' per role.'
            }
            await ctx.send(f'The command `{ctx.command}` is already being ran at its maximum of {error.number} time(s){cooldowns[error.per]} Retry a bit later.')
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
                    pass
            return

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            await ctx.send(f'You are missing the following permissions required to run the command `{ctx.command}`.\n{permissions}')
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'You missed the `{error.param.name}` parameter for the command `{ctx.command}`. '
                           f'Use `{self.bot.config.prefix}help {ctx.command}` for more information on what parameters to use.')
            return

        error_messages = {
            exceptions.ArgumentError: f'{error}',
            exceptions.ImageError: f'{error}',
            exceptions.VoiceError: f'{error}',
            commands.CheckFailure: f'{error}',
            NodeNotFound: f'There are no lavalink nodes available right now.',
            commands.TooManyArguments: f'You used too many parameters for the command `{ctx.command}`. Use `{self.bot.config.prefix}help {ctx.command}` for '
                                       f'more information on what parameters to use.',
            commands.BadArgument: f'I was unable to understand a parameter that you used for the command `{ctx.command}`. '
                                  f'Use `{self.bot.config.prefix}help {ctx.command}` for more information on what parameters to use.',
            commands.BadUnionArgument: f'I was unable to understand a parameter that you used for the command `{ctx.command}`. '
                                       f'Use `{self.bot.config.prefix}help {ctx.command}` for more information on what parameters to use.',
            commands.NoPrivateMessage: f'The command `{ctx.command}` can not be used in private messages.',
            commands.NotOwner: f'The command `{ctx.command}` is owner only.',
            commands.NSFWChannelRequired: f'The command `{ctx.command}` can only be ran in a NSFW channel.',
            commands.DisabledCommand: f'The command `{ctx.command}` has been disabled.',
            commands.ExpectedClosingQuoteError: f'You missed a closing quote in the parameters passed to the `{ctx.command}` command.',
            commands.UnexpectedQuoteError: f'There was an unexpected quote in the parameters passed to the `{ctx.command}` command.'
        }

        error_message = error_messages.get(type(error), None)
        if error_message is not None:
            await ctx.send(error_message)
            return

        await ctx.send(f'Something went wrong while executing that command. Please use `{self.bot.config.prefix}support` for more help or information.')

        formatter = prettify_exceptions.DefaultFormatter()

        formatter.theme['_ansi_enabled'] = True
        print(f'\n{"".join(formatter.format_exception(type(error), error, error.__traceback__)).strip()}\n')

        time = self.bot.utils.format_datetime(time=datetime.now())
        guild = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n' if ctx.guild else ''
        info = f'Error in command `{ctx.command}`\n\n{guild}`Channel:` {ctx.channel} `{ctx.channel.id}`\n`Author:` {ctx.author} `{ctx.author.id}`\n`Time:` {time}'

        embed = discord.Embed(colour=ctx.colour, description=f'{ctx.message.content}')
        embed.add_field(name='Info:', value=info)

        await self.bot.errors_webhook.send(embed=embed, username=f'{ctx.author}',
                                           avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

        formatter.theme['_ansi_enabled'] = False
        traceback = "".join(formatter.format_exception(type(error), error, error.__traceback__)).strip()

        if len(traceback) > 2000:
            async with self.bot.session.post('https://mystb.in/documents', data=traceback) as response:
                response = await response.json()
            traceback = f'https://mystb.in/{response["key"]}.python'
        else:
            traceback = f'```\n{traceback}\n```'

        await self.bot.errors_webhook.send(content=f'{traceback}', username=f'{ctx.author}',
                                           avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png')))

    @commands.Cog.listener()
    async def on_socket_response(self, message: dict) -> None:

        event = message.get('t', 'None')
        if event is not None:
            self.bot.socket_stats[event] += 1


def setup(bot):
    bot.add_cog(Events(bot))
