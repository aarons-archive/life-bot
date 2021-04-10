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

import collections

import discord
import psutil
from discord.ext import commands
from discord.ext.alternatives import guild_converter

import time
from bot import Life
from utilities import context, converters, exceptions, utils


class Information(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.FEATURES = {
            'VIP_REGIONS':                      'Has VIP voice regions',
            'VANITY_URL':                       'Can have vanity invite',
            'INVITE_SPLASH':                    'Can have invite splash',
            'VERIFIED':                         'Is verified server',
            'PARTNERED':                        'Is partnered server',
            'MORE_EMOJI':                       'Can have 50+ emoji (No boosts)',
            'DISCOVERABLE':                     'Is discoverable',
            'FEATURABLE':                       'Is featurable',
            'COMMUNITY':                        'Is community server',
            'COMMERCE':                         'Can have store channels',
            'PUBLIC':                           'Is public',
            'NEWS':                             'Can have news channels',
            'BANNER':                           'Can have banner',
            'ANIMATED_ICON':                    'Can have animated icon',
            'PUBLIC_DISABLED':                  'Can not be public',
            'WELCOME_SCREEN_ENABLED':           'Can have welcome screen',
            'MEMBER_VERIFICATION_GATE_ENABLED': 'Has a member verify gate',
            'PREVIEW_ENABLED':                  'Is previewable',
        }

        self.MFA_LEVELS = {
            0: 'Not required',
            1: 'Required'
        }

        self.COLOURS = {
            discord.Status.online:    0x008000,
            discord.Status.idle:      0xFF8000,
            discord.Status.dnd:       0xFF0000,
            discord.Status.offline:   0x808080,
            discord.Status.invisible: 0x808080,
        }

        self.VERIFICATION_LEVELS = {
            discord.VerificationLevel.none:    'None - No criteria set.',
            discord.VerificationLevel.low:     'Low - Must have a verified email.',
            discord.VerificationLevel.medium:  'Medium - Must have a verified email and be registered on discord for more than 5 minutes.',
            discord.VerificationLevel.high:    'High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more than 10 '
                                               'minutes.',
            discord.VerificationLevel.extreme: 'Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for more than 10 '
                                               'minutes, and a have a verified phone number.'
        }

        self.CONTENT_FILTER_LEVELS = {
            discord.ContentFilter.disabled:    'None',
            discord.ContentFilter.no_role:     'No roles',
            discord.ContentFilter.all_members: 'All members',
        }

    @commands.command(name='stats')
    async def stats(self, ctx: context.Context) -> None:
        """
        Display the bots stats.
        """

        # noinspection PyUnresolvedReferences
        uptime = utils.format_seconds(seconds=round(time.time() - self.bot.start_time), friendly=True)
        files, functions, lines, classes = utils.line_count()

        embed = discord.Embed(colour=ctx.colour)
        embed.add_field(name='Bot info:',
                        value=f'`Uptime:` {uptime}\n`Guilds:` {len(self.bot.guilds)}\n`Shards:` {len(self.bot.shards)}\n`Users:` {len(self.bot.users)}\n')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Bot stats:',
                        value=f'`Discord.py:` {discord.__version__}\n`Extensions:` {len(self.bot.extensions)}\n`Commands:` {len(self.bot.commands)}\n`Cogs:` {len(self.bot.cogs)}')

        embed.add_field(name='Code:',
                        value=f'`Functions:` {functions}\n`Classes:` {classes}\n`Lines:` {lines}\n`Files:` {files}\n')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Ping:',
                        value=f'`Latency:` {round(self.bot.latency * 1000)}ms')

        embed.set_footer(text=f'Created on {utils.format_datetime(datetime=self.bot.user.created_at)}')
        await ctx.send(embed=embed)

    @commands.command(name='system', aliases=['sys'])
    async def system(self, ctx: context.Context) -> None:
        """
        Display the bot's system stats.
        """

        embed = discord.Embed(colour=ctx.colour)
        embed.add_field(name='System CPU:',
                        value=f'`Frequency:` {round(psutil.cpu_freq().current, 2)} Mhz\n`Cores:` {psutil.cpu_count()}\n'
                              f'`Usage:` {psutil.cpu_percent(interval=0.1)}%')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='System Memory:',
                        value=f'`Available:` {round(psutil.virtual_memory().available / 1048576)} MB\n`Total:` {round(psutil.virtual_memory().total / 1048576)} MB\n'
                              f'`Used:` {round(psutil.virtual_memory().used / 1048576)} MB')

        embed.add_field(name='System Disk:',
                        value=f'`Total:` {round(psutil.disk_usage("/").total / 1073741824, 2)} GB\n`Used:` {round(psutil.disk_usage("/").used / 1073741824, 2)} GB\n'
                              f'`Free:` {round(psutil.disk_usage("/").free / 1073741824, 2)} GB')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Process information:',
                        value=f'`Memory usage:` {round(self.bot.process.memory_full_info().rss / 1048576, 2)} MB\n`CPU usage:` {self.bot.process.cpu_percent(interval=None)}%\n'
                              f'`Threads:` {self.bot.process.num_threads()}')

        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx: context.Context) -> None:
        """
        Display the bot's latency.
        """

        await ctx.send(f'{round(self.bot.latency * 1000)}ms')

    @commands.command(name='server', aliases=['serverinfo'])
    async def server(self, ctx: context.Context, *, guild: guild_converter.Guild = None) -> None:
        """
        Display information about a server.

        `guild`: The server of which to get information for. Can be its ID or Name. Defaults to the current server.
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
        for feature, description in sorted(self.FEATURES.items(), key=lambda kv: kv[1][0]):
            if feature in guild.features:
                features.append(f'<:tick:739315349715026001> {description}')
            else:
                features.append(f'<:cross:739315361811267594> {description}')

        embed = discord.Embed(colour=ctx.colour, title=f'`{guild.name}`\'s information.')
        embed.description = f'`Owner:` {guild.owner}\n' \
                            f'`Created on:` {utils.format_datetime(datetime=guild.created_at)}\n' \
                            f'`Created:` {utils.format_difference(datetime=guild.created_at)} ago\n' \
                            f'`Members:` {guild.member_count} | ' \
                            f'<:online:737824551471284356>{statuses[discord.Status.online]} | <:away:627627415119724554>{statuses[discord.Status.idle]} | ' \
                            f'<:dnd:627627404784828416>{statuses[discord.Status.dnd]} | <:offline:627627415144890389>{statuses[discord.Status.offline]}\n' \
                            f'`Content filter level:` {self.CONTENT_FILTER_LEVELS[ctx.guild.explicit_content_filter]} | ' \
                            f'`2FA:` {self.MFA_LEVELS[ctx.guild.mfa_level]}\n' \
                            f'`Verification level:` {self.VERIFICATION_LEVELS[ctx.guild.verification_level]}\n'

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
        await ctx.send(embed=embed)

    @commands.command(name='role', aliases=['roleinfo'])
    async def role(self, ctx: context.Context, *, role: discord.Role = None) -> None:
        """
        Displays information about a role.

        `role`: The role to display information of. Can be its @Mention, ID or Name.
        """

        if not role:
            if not ctx.guild:
                raise exceptions.ArgumentError('You must be in a guild to use this command without passing the `role` argument.')
            role = ctx.author.top_role

        embed = discord.Embed(colour=ctx.colour, title=f'Information about the role `{role}`')
        embed.set_footer(text=f'ID: {role.id}')
        embed.description = f'`Name:` {role.name}\n' \
                            f'`Hoisted:` {role.hoist}\n' \
                            f'`Position (from bottom):` {role.position}\n' \
                            f'`Managed:` {role.managed}\n' \
                            f'`Mentionable:` {role.mentionable}\n' \
                            f'`Colour:` {str(role.colour).upper()}\n' \
                            f'`Created at:` {utils.format_datetime(datetime=role.created_at)}\n' \
                            f'`Members with this role:` {len(role.members)}'

        await ctx.send(embed=embed)

    @commands.command(name='rolecounts', aliases=['rcs', 'roles'])
    async def role_counts(self, ctx: context.Context) -> None:
        """
        Displays a list of roles and how many people have that role.
        """

        counts = {role.name.title(): len(role.members) for role in ctx.guild.roles}
        counts['Bots (Actual)'] = len([member for member in ctx.guild.members if member.bot])

        roles = [f'{role_name[:20] + (role_name[20:] and ".."):23} | {role_count}' for role_name, role_count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]
        await ctx.paginate(entries=roles, per_page=20, codeblock=True)

    @commands.command(name='channels')
    async def channels(self, ctx: context.Context, *, guild: guild_converter.Guild = None) -> None:
        """
        Displays a list of a servers channels.

        `guild`: The server of which to display channels for. Can be its ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        channels = [channel for channel in guild.channels if not isinstance(channel, discord.CategoryChannel) and not channel.category]
        categories = [category for category in guild.channels if isinstance(category, discord.CategoryChannel)]

        entries = [
            f'{utils.channel_emoji(channel=channel)}{channel}'
            for channel in sorted(channels, key=lambda channel: channel.position)
        ]

        space = '\u200b ' * 5
        for category in sorted(categories, key=lambda category: category.position):
            entries.append(f'<:category:738960756233601097> **{category}**')
            for channel in category.channels:
                entries.append(f'{space}{utils.channel_emoji(channel=channel)}{channel}')

        await ctx.paginate_embed(entries=entries, per_page=30, title=f'`{guild.name}`\'s channels.')

    @commands.command(name='icon')
    async def icon(self, ctx: context.Context, *, guild: guild_converter.Guild = None) -> None:
        """
        Displays a server's icon.

        `guild`: The server of which to get the icon for. Can be its ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.icon:
            raise exceptions.ArgumentError(f'The server `{guild.name}` does not have an icon.')

        embed = discord.Embed(colour=ctx.colour, title=f'`{guild.name}`\'s icon')
        embed.description = f'[PNG]({guild.icon_url_as(format="png")}) | [JPEG]({guild.icon_url_as(format="jpeg")}) | [WEBP]({guild.icon_url_as(format="webp")})'
        embed.set_image(url=str(guild.icon_url_as(format='png')))

        if guild.is_icon_animated():
            embed.description += f' | [GIF]({guild.icon_url_as(format="gif")})'
            embed.set_image(url=str(guild.icon_url_as(format='gif')))

        await ctx.send(embed=embed)

    @commands.command(name='banner')
    async def banner(self, ctx: context.Context, *, guild: guild_converter.Guild = None) -> None:
        """
        Displays a servers banner.

        `guild`: The server of which to get the banner for. Can be its ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.banner:
            raise exceptions.ArgumentError(f'The server `{guild.name}` does not have a banner.')

        embed = discord.Embed(colour=ctx.colour, title=f'`{guild.name}`\'s banner')
        embed.description = f'[PNG]({guild.banner_url_as(format="png")}) | [JPEG]({guild.banner_url_as(format="jpeg")}) | [WEBP]({guild.banner_url_as()})'
        embed.set_image(url=str(guild.banner_url_as(format='png')))

        await ctx.send(embed=embed)

    @commands.command(name='splash')
    async def splash(self, ctx: context.Context, *, guild: guild_converter.Guild = None) -> None:
        """
        Displays a servers splash.

        `guild`: The server of which to get the splash for. Can be its ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.splash:
            raise exceptions.ArgumentError(f'The server `{guild.name}` does not have an splash.')

        embed = discord.Embed(colour=ctx.colour, title=f'`{guild.name}`\'s splash')
        embed.description = f'[PNG]({guild.splash_url_as(format="png")}) | [JPEG]({guild.splash_url_as(format="jpeg")}) | [WEBP]({guild.splash_url_as()})'
        embed.set_image(url=str(guild.splash_url_as(format='png')))

        await ctx.send(embed=embed)

    @commands.command(name='member', aliases=['memberinfo'])
    async def member(self, ctx: context.Context, *, member: discord.Member = None) -> None:
        """
        Displays a member's account information.

        `member`: The member of which to get information for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.COLOURS[member.status], title=f'`{member}`\'s information.')
        embed.description = f'`Discord Name:` {member} {"<:owner:738961071729278987>" if member.id == member.guild.owner.id else ""}\n' \
                            f'`Created on:` {utils.format_datetime(datetime=member.created_at)}\n' \
                            f'`Created:` {utils.format_difference(datetime=member.created_at)} ago\n' \
                            f'`Badges:` {utils.badges(bot=self.bot, person=member)}\n' \
                            f'`Status:` {member.status.name.replace("dnd", "Do Not Disturb").title()}{"<:phone:738961150343118958>" if member.is_on_mobile() else ""}\n' \
                            f'`Bot:` {str(member.bot).replace("True", "Yes").replace("False", "No")}\n' \
                            f'`Activity:` {utils.activities(person=member)}'

        embed.add_field(name='Server related information:',
                        value=f'`Server nickname:` {member.nick}\n'
                              f'`Joined on:` {utils.format_datetime(datetime=member.joined_at)}\n'
                              f'`Joined:` {utils.format_difference(datetime=member.joined_at)} ago\n'
                              f'`Join Position:` {sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1}\n'
                              f'`Top role:` {member.top_role.mention}\n'
                              f'`Role count:` {len(member.roles) - 1}', inline=False)

        embed.set_footer(text=f'ID: {member.id}')
        await ctx.send(embed=embed)

    @commands.command(name='user', aliases=['userinfo'])
    async def user(self, ctx: context.Context, *, user: converters.UserConverter = None) -> None:
        """
        Displays a user's account information.

        `user`: The user of which to get information for. Can be their ID or Username. Defaults to you.
        """

        if not user:
            user = await self.bot.fetch_user(ctx.author.id)

        embed = discord.Embed(colour=ctx.colour, title=f'`{user}`\'s information:')
        embed.description = f'`Discord name:` {user}\n' \
                            f'`Created on:` {utils.format_datetime(datetime=user.created_at)}\n' \
                            f'`Created:` {utils.format_difference(datetime=user.created_at)} ago\n' \
                            f'`Badges:` {utils.badges(bot=self.bot, person=user)}\n' \
                            f'`Bot:` {str(user.bot).replace("True", "Yes").replace("False", "No")}'

        embed.set_footer(text=f'ID: {user.id}')
        await ctx.send(embed=embed)

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx: context.Context, *, user: converters.UserConverter = None) -> None:
        """
        Display a user's avatar.

        `user`: The user of which to get the avatar for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not user:
            user = ctx.author

        embed = discord.Embed(colour=ctx.colour, title=f'`{user}`\'s avatar:')
        embed.description = f'[PNG]({user.avatar_url_as(format="png")}) | [JPEG]({user.avatar_url_as(format="jpeg")}) | [WEBP]({user.avatar_url_as(format="webp")})'
        embed.set_image(url=str(user.avatar_url_as(format='png')))

        if user.is_avatar_animated():
            embed.description += f' | [GIF]({user.avatar_url_as(format="gif")})'
            embed.set_image(url=str(user.avatar_url_as(format='gif')))

        await ctx.send(embed=embed)


def setup(bot: Life) -> None:
    bot.add_cog(Information(bot=bot))
