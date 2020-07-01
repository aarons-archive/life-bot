"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import inspect
import os
import time
from datetime import datetime

import discord
import psutil
from discord.ext import commands
from tabulate import tabulate


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.support_url = 'https://discord.gg/xP8xsHr'
        self.bot.source_url = 'https://github.com/iDevision/Life'
        self.bot.upvote_url = 'https://top.gg/bot/628284183579721747'
        self.bot.invite_url = f'https://discord.com/oauth2/authorize?client_id=' \
                              f'628284183579721747&scope=bot&permissions=103926848'

    @commands.command(name='info')
    async def info(self, ctx):
        """
        Get information about the bot.
        """

        return await ctx.send("soon:tm:")

    @commands.command(name='stats')
    async def stats(self, ctx):
        """
        Display the bots stats.
        """

        uyviyvy
        latency_ms, typing_ms, discord_ms = await self.bot.utils.ping(ctx)
        uptime = self.bot.utils.format_time(seconds=round(time.time() - self.bot.start_time), friendly=True)
        files, functions, lines, classes = self.bot.utils.linecount()

        embed = discord.Embed(colour=discord.Color.gold())
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
                        value=f'`Latency:` {latency_ms}\n`Discord:` {discord_ms}\n`Typing:` {typing_ms}')

        embed.add_field(name='Links:',
                        value=f'`[Invite me]({self.bot.invite_url}) | [Support server]({self.bot.support_url}) | '
                              f'[Source code]({self.bot.source_url}) | [Upvote me]({self.bot.upvote_url})`')

        embed.set_footer(text=f'Created on {datetime.strftime(self.bot.user.created_at, "%A %d %B %Y at %H:%M")}')
        return await ctx.send(embed=embed)

    @commands.command(name='system', aliases=['sys'])
    async def system(self, ctx):
        """
        Display the bots system stats.
        """

        embed = discord.Embed(colour=discord.Color.gold())
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
    async def ping(self, ctx):
        """
        Display the bots latency.
        """

        latency_ms, typing_ms, discord_ms = await self.bot.utils.ping(ctx)
        table = tabulate(tabular_data=[['Type', 'Ping'], ['Latency', latency_ms],
                                       ['Discord', discord_ms], ['Typing', typing_ms]],
                         headers='firstrow', tablefmt='psql')
        return await ctx.send(f'```py\n{table}\n```')

    @commands.command(name='support')
    async def support(self, ctx):
        """
        Get an invite link to the bots support server.
        """

        return await ctx.send(f'If you have any problems with the bot or if you have any suggestions/feedback be '
                              f'sure to join the support server using this link {self.bot.support_url}')

    @commands.command(name='source', aliases=["src"])
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link to the source of a command.

        `command`: The command to get the source of.
        """

        if command is None:
            return await ctx.send(f'<https://github.com/iDevision/Life>')

        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send('I could not find that command.')

        if isinstance(command, self.bot.help_command._command_impl.__class__):
            command_obj = type(self.bot.help_command)
            file_path = os.path.relpath(inspect.getsourcefile(command_obj))
        else:
            command_obj = command.callback
            file_path = os.path.relpath(command_obj.__code__.co_filename)

        lines, first_line = inspect.getsourcelines(command_obj)
        last_line = first_line + (len(lines) - 1)

        link = f'<https://github.com/iDevision/Life/blob/master/Life/{file_path}#L{first_line}-L{last_line}>'
        return await ctx.send(link)

    @commands.command(name='serverinfo', aliases=['server'])
    async def serverinfo(self, ctx):
        """
        Get information about the server.
        """

        statuses = self.bot.utils.guild_member_status(ctx.guild)

        embed = discord.Embed(colour=discord.Color.gold(), title=f"{ctx.guild.name}'s stats and information.")
        embed.description = ctx.guild.description if ctx.guild.description else None
        embed.add_field(name='General information:',
                        value=f'`Owner:` {ctx.guild.owner}\n'
                              f'`Created at:` {datetime.strftime(ctx.guild.created_at, "%A %d %B %Y at %H:%M")}\n'
                              f'`Members:` {ctx.guild.member_count} |'
                              f'<:online:627627415224713226>{statuses["online"]} |'
                              f'<:away:627627415119724554>{statuses["idle"]} |'
                              f'<:dnd:627627404784828416>{statuses["dnd"]} |'
                              f'<:offline:627627415144890389>{statuses["offline"]}\n'
                              f'`Nitro Tier:` {ctx.guild.premium_tier} | '
                              f'`Boosters:` {ctx.guild.premium_subscription_count}\n'
                              f'`File Size:` {round(ctx.guild.filesize_limit / 1048576)} MB | '
                              f'`Bitrate:` {round(ctx.guild.bitrate_limit / 1000)} kbps | '
                              f'`Emoji:` {ctx.guild.emoji_limit}\n'
                              f'`Content filter level:` {self.bot.utils.content_filter_level(ctx.guild)} | '
                              f'`2FA:` {self.bot.utils.mfa_level(ctx.guild)}\n'
                              f'`Verification level:` {self.bot.utils.verification_level(ctx.guild)}\n', inline=False)

        embed.add_field(name='`Channels:`',
                        value=f'`AFK timeout:` {int(ctx.guild.afk_timeout / 60)}m | '
                              f'`AFK channel:` {ctx.guild.afk_channel}\n'
                              f'`Text channels:` {len(ctx.guild.text_channels)} | '
                              f'`Voice channels:` {len(ctx.guild.voice_channels)}\n'
                              f'`Voice region:` {self.bot.utils.guild_region(ctx.guild)}\n', inline=False)

        embed.set_thumbnail(url=self.bot.utils.guild_icon(ctx.guild))
        embed.set_image(url=self.bot.utils.guild_banner(ctx.guild))
        embed.set_footer(text=f'ID: {ctx.guild.id}')

        return await ctx.send(embed=embed)

    @commands.command(name='servericon', aliases=['icon'])
    async def servericon(self, ctx):
        """
        Display the servers icon.
        """

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"{ctx.guild.name}'s icon",
            description=f'[PNG]({ctx.guild.icon_url_as(size=1024, format="png")}) | ' 
                        f'[JPEG]({ctx.guild.icon_url_as(size=1024, format="jpeg")}) | '
                        f'[WEBP]({ctx.guild.icon_url_as(size=1024, format="webp")})'
        )

        if ctx.guild.is_icon_animated():
            embed.description += f' | [GIF]({ctx.guild.icon_url_as(size=1024, format="gif")})'
            embed.set_image(url=str(ctx.guild.icon_url_as(size=1024, format='gif')))
        else:
            embed.set_image(url=str(ctx.guild.icon_url_as(size=1024, format='png')))

        return await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user'])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """
        Get information about you, or a specified member.

        `member`: The member to get information from. Can be a Mention, Name or ID.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.bot.utils.member_colour(ctx.author))
        embed.title = f"{member}'s stats and information."
        embed.add_field(name='General information:',
                        value=f'`Discord Name:` {member}\n'
                              f'`Created at:` {datetime.strftime(member.created_at, "%A %d %B %Y at %H:%M")}\n'
                              f'`Status:` {self.bot.utils.member_status(member)}\n'
                              f'`Activity:` {self.bot.utils.member_activity(member)}', inline=False)

        embed.add_field(name='Server-related information:',
                        value=f'`Joined server:` {datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}\n'
                              f'`Nickname:` {member.nick}\n'
                              f'`Top role:` {member.top_role.mention}', inline=False)

        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        embed.set_footer(text=f'ID: {member.id}')

        return await ctx.send(embed=embed)

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx, *, member: discord.Member = None):
        """
        Display yours, or a specified members avatar.

        `member`: The member to get the avatar of. Can be a Mention, Name or ID.
        """

        if not member:
            member = ctx.author

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"{member.name}'s avatar",
            description=f'[PNG]({member.avatar_url_as(size=1024, format="png")}) | ' 
                        f'[JPEG]({member.avatar_url_as(size=1024, format="jpeg")}) | '
                        f'[WEBP]({member.avatar_url_as(size=1024, format="webp")})'
        )

        if member.is_avatar_animated():
            embed.description += f' | [GIF]({member.avatar_url_as(size=1024, format="gif")})'
            embed.set_image(url=f'{member.avatar_url_as(size=1024, format="gif")}')
        else:
            embed.set_image(url=f'{member.avatar_url_as(size=1024, format="png")}')

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
