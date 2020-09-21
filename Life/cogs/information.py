"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import codecs
import collections
import datetime as dt
import inspect
import os
import pathlib
import time
import typing

import discord
import psutil
from discord.ext import commands
from discord.ext.alternatives import guild_converter

from bot import Life
from utilities import context, converters, exceptions


class Information(commands.Cog):

    def __init__(self, bot: Life):
        self.bot = bot

    @commands.command(name='info', aliases=['about'])
    async def info(self, ctx: context.Context):
        """
        Get information about the bot.
        """

        return await ctx.send("soon:tm:")

    @commands.command(name='stats')
    async def stats(self, ctx: context.Context):
        """
        Display the bots stats.
        """

        uptime = self.bot.utils.format_seconds(seconds=round(time.time() - self.bot.start_time), friendly=True)

        files, functions, lines, classes = 0, 0, 0, 0
        docstring = False

        for dirpath, dirname, filenames in os.walk('.'):

            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                files += 1

                with codecs.open('./' + str(pathlib.PurePath(dirpath, filename)), 'r', 'utf-8') as filelines:
                    filelines = [line.strip() for line in filelines]
                    for line in filelines:
                        if len(line) == 0:
                            continue

                        if line.startswith('"""'):
                            if docstring is False:
                                docstring = True
                            else:
                                docstring = False
                        if docstring is True:
                            continue

                        if line.startswith('#'):
                            continue
                        if line.startswith(('def', 'async def')):
                            functions += 1
                        if line.startswith('class'):
                            classes += 1
                        lines += 1

        embed = discord.Embed(colour=ctx.colour)
        embed.add_field(name='Bot info:',
                        value=f'`Uptime:` {uptime}\n`Guilds:`{len(self.bot.guilds)}\n'
                              f'`Shards:` {len(self.bot.shards)}\n`Users:` {len(self.bot.users)}\n')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Bot stats:',
                        value=f'`Discord.py:` {discord.__version__}\n`Extensions:` {len(self.bot.extensions)}\n'
                              f'`Commands:` {len(self.bot.commands)}\n`Cogs:` {len(self.bot.cogs)}')

        embed.add_field(name='Code:',
                        value=f'`Functions:` {functions}\n`Classes:` {classes}\n'
                              f'`Lines:` {lines}\n`Files:` {files}\n')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Ping:',
                        value=f'`Latency:` {round(self.bot.latency * 1000)}ms')

        embed.add_field(name='Links:',
                        value=f'[Invite me]({self.bot.invite}) | [Support server]({self.bot.support}) | '
                              f'[Source code]({self.bot.github})')

        embed.set_footer(text=f'Created on {dt.datetime.strftime(self.bot.user.created_at, "%A %d %B %Y at %H:%M")}')
        return await ctx.send(embed=embed)

    @commands.command(name='system', aliases=['sys'])
    async def system(self, ctx: context.Context):
        """
        Display the bots system stats.
        """

        embed = discord.Embed(colour=ctx.colour)
        embed.add_field(name='System CPU:',
                        value=f'`Frequency:` {round(psutil.cpu_freq().current, 2)} Mhz\n'
                              f'`Cores:` {psutil.cpu_count()}\n'
                              f'`Usage:` {psutil.cpu_percent(interval=0.1)}%')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='System Memory:',
                        value=f'`Available:` {round(psutil.virtual_memory().available / 1048576)} MB\n'
                              f'`Total:` {round(psutil.virtual_memory().total / 1048576)} MB\n'
                              f'`Used:` {round(psutil.virtual_memory().used / 1048576)} MB')

        embed.add_field(name='System Disk:',
                        value=f'`Total:` {round(psutil.disk_usage("/").total / 1073741824, 2)} GB\n'
                              f'`Used:` {round(psutil.disk_usage("/").used / 1073741824, 2)} GB\n'
                              f'`Free:` {round(psutil.disk_usage("/").free / 1073741824, 2)} GB')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Process information:',
                        value=f'`Memory usage:` {round(self.bot.process.memory_full_info().rss / 1048576, 2)} MB\n'
                              f'`CPU usage:` {self.bot.process.cpu_percent(interval=None)}%\n'
                              f'`Threads:` {self.bot.process.num_threads()}')

        return await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx: context.Context):
        """
        Display the bots latency.
        """

        return await ctx.send(f'{round(self.bot.latency * 1000)}ms')

    @commands.command(name='support')
    async def support(self, ctx: context.Context):
        """
        Get an invite link to the bots support server.
        """

        return await ctx.send(f'If you have any problems with the bot or if you have any suggestions/feedback be sure to join the support server using this '
                              f'link {self.support}')

    @commands.command(name='invite')
    async def support(self, ctx: context.Context):
        """
        Get a link the invite the bot.
        """

        return await ctx.send(f'You can invite the bot here <{self.bot.invite}>')

    @commands.command(name='source')
    async def source(self, ctx: context.Context, *, command: str = None):
        """
        Get a github link to the source of a command.

        `command`: The command to get the source for.
        """

        if command is None:
            return await ctx.send(f'<{self.bot.github}>')

        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send('I could not find that command.')

        # noinspection PyProtectedMember
        if isinstance(command, self.bot.help_command._command_impl.__class__):
            command_obj = type(self.bot.help_command)
            file_path = os.path.relpath(inspect.getsourcefile(command_obj))
        else:
            command_obj = command.callback
            file_path = os.path.relpath(command_obj.__code__.co_filename)

        lines, first_line = inspect.getsourcelines(command_obj)
        last_line = first_line + (len(lines) - 1)

        link = f'<{self.bot.github}/blob/master/Life/{file_path}#L{first_line}-L{last_line}>'
        return await ctx.send(link)

    @commands.command(name='icon')
    async def icon(self, ctx: context.Context, *, guild: guild_converter.Guild = None):
        """
        Displays a servers icon.

        `guild`: The server of which to get the icon for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.icon:
            raise exceptions.ArgumentError(f'The server `{guild}` does not have an icon.')

        embed = discord.Embed(colour=ctx.colour, title=f"{guild.name}'s icon")
        embed.description = f'[PNG]({guild.icon_url_as(format="png")}) | [JPEG]({guild.icon_url_as(format="jpeg")}) | [WEBP]({guild.icon_url_as(format="webp")})'
        embed.set_image(url=str(guild.icon_url_as(format='png')))

        if guild.is_icon_animated():
            embed.description += f' | [GIF]({guild.icon_url_as(format="gif")})'
            embed.set_image(url=str(guild.icon_url_as(size=1024, format='gif')))

        return await ctx.send(embed=embed)

    @commands.command(name='banner')
    async def banner(self, ctx: context.Context, *, guild: guild_converter.Guild = None):
        """
        Displays a servers banner.

        `guild`: The server of which to get the banner for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.banner:
            raise exceptions.ArgumentError(f'The server `{guild}` does not have a banner.')

        embed = discord.Embed(colour=ctx.colour, title=f"{guild.name}'s banner")
        embed.description = f'[PNG]({guild.banner_url_as(format="png")}) | [JPEG]({guild.banner_url_as(format="jpeg")}) | [WEBP]({guild.banner_url_as(format="webp")})'
        embed.set_image(url=str(guild.banner_url_as(format='png')))

        return await ctx.send(embed=embed)

    @commands.command(name='splash')
    async def splash(self, ctx: context.Context, *, guild: guild_converter.Guild = None):
        """
        Displays a servers splash.

        `guild`: The server of which to get the splash for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.splash:
            raise exceptions.ArgumentError(f'The server `{guild}` does not have an splash.')

        embed = discord.Embed(colour=ctx.colour, title=f"{guild.name}'s splash")
        embed.description = f'[PNG]({guild.splash_url_as(format="png")}) | [JPEG]({guild.splash_url_as(format="jpeg")}) | [WEBP]({guild.splash_url_as(format="webp")})'
        embed.set_image(url=str(guild.splash_url_as(format='png')))

        return await ctx.send(embed=embed)

    @commands.command(name='server', aliases=['serverinfo'])
    async def server(self, ctx: context.Context, guild: guild_converter.Guild = None):
        """
        Display information about a server.

        `guild`: The server of which to get information for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        region = guild.region.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')
        if guild.region == discord.VoiceRegion.hongkong:
            region = 'Hong Kong'
        if guild.region == discord.VoiceRegion.southafrica:
            region = 'South Africa'

        statuses = collections.Counter([member.status for member in guild.members])

        features = []
        for feature, description in self.bot.utils.features.items():
            if feature in guild.features:
                features.append(f'<:tick:739315349715026001> {description}')
            else:
                features.append(f'<:cross:739315361811267594> {description}')

        embed = discord.Embed(colour=ctx.colour, title=f"{guild.name}'s information.")
        embed.description = f'`Owner:` {guild.owner}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=guild.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_time_difference(datetime=guild.created_at)} ago\n' \
                            f'`Members:` {guild.member_count} | ' \
                            f'<:online:737824551471284356>{statuses[discord.Status.online]} | <:away:627627415119724554>{statuses[discord.Status.idle]} | ' \
                            f'<:dnd:627627404784828416>{statuses[discord.Status.dnd]} | <:offline:627627415144890389>{statuses[discord.Status.offline]}\n' \
                            f'`Content filter level:` {self.bot.utils.content_filter_levels[ctx.guild.explicit_content_filter]} | ' \
                            f'`2FA:` {self.bot.utils.mfa_levels[ctx.guild.mfa_level]}\n' \
                            f'`Verification level:` {self.bot.utils.verification_levels[ctx.guild.verification_level]}\n'

        embed.add_field(name='Boost information:',
                        value=f'`Nitro Tier:` {ctx.guild.premium_tier} | `Boosters:` {ctx.guild.premium_subscription_count} | '
                              f'`File Size:` {round(ctx.guild.filesize_limit / 1048576)} MB | `Bitrate:` {round(ctx.guild.bitrate_limit / 1000)} kbps\n'
                              f'`Emoji limit:` {ctx.guild.emoji_limit} | `Normal emoji:` {sum([1 for emoji in guild.emojis if not emoji.animated])} | '
                              f'`Animated emoji:` {sum([1 for emoji in guild.emojis if emoji.animated])}')

        embed.add_field(name='Channels:',
                        value=f'`AFK timeout:` {int(ctx.guild.afk_timeout / 60)}m | `AFK channel:` {ctx.guild.afk_channel}\n `Voice region:` {region} | '
                              f'`Text channels:` {len(ctx.guild.text_channels)} | `Voice channels:` {len(ctx.guild.voice_channels)}\n', inline=False)

        embed.add_field(name='Features:', value='\n'.join(features[0:8]))
        embed.add_field(name='\u200b', value='\n'.join(features[8:16]))
        embed.set_footer(text=f'ID: {guild.id} | Owner ID: {guild.owner.id}')
        return await ctx.send(embed=embed)

    @commands.command(name='channels')
    async def channels(self, ctx: context.Context, *, guild: guild_converter.Guild = None):
        """
        Displays a list of a servers channels.

        `guild`: The server of which to display channels for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        entries = []

        channels = [channel for channel in guild.channels if not isinstance(channel, discord.CategoryChannel) and not channel.category]
        categories = [category for category in guild.channels if isinstance(category, discord.CategoryChannel)]

        for channel in sorted(channels, key=lambda channel: channel.position):
            entries.append(f'{await self.bot.channel_emoji_converter.convert(ctx=ctx, channel=channel)}{channel}')

        for category in sorted(categories, key=lambda category: category.position):
            entries.append(f'<:category:738960756233601097> **{category}**')
            for channel in category.channels:
                space = '\u200b ' * 4
                entries.append(f'{space}{await self.bot.channel_emoji_converter.convert(ctx=ctx, channel=channel)}{channel}')

        return await ctx.paginate_embed(entries=entries, per_page=30, title='List of channels, categories and voice channels.')

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx: context.Context, *, user: typing.Union[discord.Member, converters.User] = None):
        """
        Display a user's avatar.

        `user`: The user of which to get the avatar for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if not user:
            user = ctx.author

        embed = discord.Embed(colour=ctx.colour, title=f"{user.name}'s avatar")
        embed.description = f'[PNG]({user.avatar_url_as(format="png")}) | [JPEG]({user.avatar_url_as(format="jpeg")}) | [WEBP]({user.avatar_url_as(format="webp")})'
        embed.set_image(url=str(user.avatar_url_as(format='png')))

        if user.is_avatar_animated():
            embed.description += f' | [GIF]({user.avatar_url_as(format="gif")})'
            embed.set_image(url=str(user.avatar_url_as(format='gif')))

        return await ctx.send(embed=embed)

    @commands.command(name='user', aliases=['userinfo'])
    async def user(self, ctx: context.Context, *, user: converters.User = None):
        """
        Displays a user's basic account information.

        `user`: The user of which to get information for. Can be their ID or Username. Defaults to you.
        """

        if not user:
            user = await self.bot.fetch_user(ctx.author.id)

        embed = discord.Embed(colour=ctx.colour, title=f'{user}\'s information:')
        embed.description = f'`Discord name:` {user}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=user.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_time_difference(datetime=user.created_at)} ago\n' \
                            f'`Badges:` {self.bot.utils.badges(person=user)}\n' \
                            f'`Bot:` {str(user.bot).replace("True", "Yes").replace("False", "No")}'
        embed.set_thumbnail(url=str(user.avatar_url_as(format='gif' if user.is_avatar_animated() is True else 'png')))
        embed.set_footer(text=f'ID: {user.id}')
        return await ctx.send(embed=embed)

    @commands.command(name='member', alias=['memberinfo'])
    async def member(self, ctx: context.Context, *, member: discord.Member = None):
        """
        Displays a member's account information.

        `member`: The member of which to get information for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.bot.utils.colours[member.status], title=f'{member}\'s information.')
        embed.description = f'`Discord Name:` {member} {"<:owner:738961071729278987>" if member.id == member.guild.owner.id else ""}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=member.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_time_difference(datetime=member.created_at)} ago\n' \
                            f'`Badges:` {self.bot.utils.badges(person=member)}\n' \
                            f'`Status:` {member.status.name.replace("dnd", "Do Not Disturb").title()}' \
                            f'{"<:phone:738961150343118958>" if member.is_on_mobile() else ""}\n' \
                            f'`Bot:` {str(member.bot).replace("True", "Yes").replace("False", "No")}\n' \
                            f'`Activity:` {self.bot.utils.activities(person=member)}'

        embed.add_field(name='Server related information:',
                        value=f'`Server nickname:` {member.nick}\n'
                              f'`Joined on:` {self.bot.utils.format_datetime(datetime=member.joined_at)}\n'
                              f'`Joined:` {self.bot.utils.format_time_difference(datetime=member.joined_at)} ago\n'
                              f'`Top role:` {member.top_role.mention}\n'
                              f'`Role count:` {len(member.roles) - 1}', inline=False)

        embed.set_thumbnail(url=str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png')))
        embed.set_footer(text=f'ID: {member.id}')
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
