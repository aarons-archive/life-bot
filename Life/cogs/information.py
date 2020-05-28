import inspect
import os
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
        Get information about the bot stats.
        """

        latency_ms, average_latency_ms, typing_ms, discord_ms = await self.bot.utils.ping(ctx)
        files, functions, lines, classes = self.bot.utils.linecount()

        embed = discord.Embed(colour=discord.Color.gold())
        embed.add_field(name='__**Bot info:**__',
                        value=f'**Uptime:** {self.bot.utils.format_time(seconds=self.bot.uptime, friendly=True)}\n'
                              f'**Users:** {len(self.bot.users)}\n **Guilds:** {len(self.bot.guilds)}\n'
                              f'**Shards:** {len(self.bot.shards)}')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='__**Bot stats:**__',
                        value=f'**Discord.py Version:** {discord.__version__}\n**Commands:** {len(self.bot.commands)}\n'
                              f'**Extensions:** {len(self.bot.extensions)}\n**Cogs:** {len(self.bot.cogs)}')

        embed.add_field(name='__**Code:**__',
                        value=f'**Functions:** {functions}\n**Classes:** {classes}\n'
                              f'**Lines:** {lines}\n**Files:** {files}\n')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='__**Ping:**__',
                        value=f'**Average:** {average_latency_ms}\n**Latency:** {latency_ms}\n'
                              f'**Typing:** {typing_ms}\n**Discord:** {discord_ms}')

        embed.add_field(name='__**Links:**__',
                        value=f'**[Invite me]({self.bot.invite_url}) | [Support server]({self.bot.support_url}) | '
                              f'[Source code]({self.bot.source_url}) | [Upvote me]({self.bot.upvote_url})**')

        embed.set_footer(text=f'Created on {datetime.strftime(self.bot.user.created_at, "%A %d %B %Y at %H:%M")}')
        return await ctx.send(embed=embed)

    @commands.command(name='system', aliases=['sys'])
    async def system(self, ctx):
        """
        Get information about the bots system.
        """

        embed = discord.Embed(colour=discord.Color.gold())
        embed.add_field(name='__**System CPU:**__',
                        value=f'**Cores:** {psutil.cpu_count()}\n'
                              f'**Usage:** {psutil.cpu_percent(interval=0.1)}%\n'
                              f'**Frequency:** {round(psutil.cpu_freq().current, 2)} Mhz')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='__**System Memory:**__',
                        value=f'**Total:** {round(psutil.virtual_memory().total / 1048576)} MB\n'
                              f'**Used:** {round(psutil.virtual_memory().used / 1048576)} MB\n'
                              f'**Available:** {round(psutil.virtual_memory().available / 1048576)} Mb')

        embed.add_field(name='__**System Disk:**__',
                        value=f'**Total:** {round(psutil.disk_usage("/").total / 1073741824, 2)} GB\n'
                              f'**Used:** {round(psutil.disk_usage("/").used / 1073741824, 2)} GB\n'
                              f'**Free:** {round(psutil.disk_usage("/").free / 1073741824, 2)} GB')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='__**Process information:**__',
                        value=f'**Memory usage:** {round(self.bot.process.memory_full_info().rss / 1048576, 2)} MB\n'
                              f'**CPU usage:** {self.bot.process.cpu_percent(interval=None)}%\n'
                              f'**Threads:** {self.bot.process.num_threads()}')

        return await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Display the bots latency.
        """

        latency_ms, average_latency_ms, typing_ms, discord_ms = await self.bot.utils.ping(ctx)
        table = tabulate(tabular_data=[['Type', 'Ping'],
                                       ['Average', average_latency_ms], ['Latency', latency_ms],
                                       ['Typing', typing_ms], ['Discord', discord_ms]],
                         headers='firstrow', tablefmt='psql')
        return await ctx.send(f'```py\n{table}\n```')

    @commands.command(name='support')
    async def support(self, ctx):
        """
        Gets an invite link to the bots support server.
        """

        return await ctx.send(f'If you have any problems with the bot or if you have any suggestions/feedback be '
                              f'sure to join the support server using this link {self.bot.support_url}')

    @commands.command(name='source')
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link to the source of a command

        `command`: The command to get the source of.
        """

        if command is None:
            return await ctx.send(f'<https://github.com/iDevision/Life>')

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('I could not find that command.')

        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)

        location = ''
        if not obj.callback.__module__.startswith('discord'):
            location = os.path.relpath(src.co_filename).replace('\\', '/')

        return await ctx.send(f'<https://github.com/iDevision/Life/blob/master/'
                              f'Life/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>')

    @commands.command(name='avatar', alisases=['avy', 'av'])
    async def avatar(self, ctx, *, member: discord.Member = None):
        """
        Get yours or a specified members avatar.

        `member`: The member to get the avatar of. Can be a Mention, Name or ID. If none it will display your avatar.
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

    @commands.command(name='icon', alisases=['guild_icon'])
    async def icon(self, ctx):
        """
        Get the current servers icon.
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

    @commands.command(name='serverinfo', aliases=['server', 'guildinfo', 'guild'])
    async def serverinfo(self, ctx):
        """
        Get information about the server.
        """

        statuses = self.bot.utils.guild_member_status(ctx.guild)

        embed = discord.Embed(colour=discord.Color.gold())
        embed.title = f"{ctx.guild.name}'s stats and information."
        embed.description = ctx.guild.description if ctx.guild.description else None
        embed.add_field(name='__**General information:**__',
                        value=f'**Owner:** {ctx.guild.owner}\n'
                              f'**Created at:** {datetime.strftime(ctx.guild.created_at, "%A %d %B %Y at %H:%M")}\n'
                              f'**Members:** {ctx.guild.member_count} |'
                              f'<:online:627627415224713226>{statuses["online"]} |'
                              f'<:away:627627415119724554>{statuses["idle"]} |'
                              f'<:dnd:627627404784828416>{statuses["dnd"]} |'
                              f'<:offline:627627415144890389>{statuses["offline"]}\n'
                              f'**Nitro Tier:** {ctx.guild.premium_tier} | '
                              f'**Boosters:** {ctx.guild.premium_subscription_count}\n'
                              f'**File Size:** {round(ctx.guild.filesize_limit / 1048576)} MB | '
                              f'**Bitrate:** {round(ctx.guild.bitrate_limit / 1000)} kbps | '
                              f'**Emoji:** {ctx.guild.emoji_limit}\n'
                              f'**Content filter level:** {self.bot.utils.content_filter_level(ctx.guild)} | '
                              f'**2FA:** {self.bot.utils.mfa_level(ctx.guild)}\n'
                              f'**Verification level:** {self.bot.utils.verification_level(ctx.guild)}\n', inline=False)

        embed.add_field(name='__**Channels:**__',
                        value=f'**AFK timeout:** {int(ctx.guild.afk_timeout / 60)}m | '
                              f'**AFK channel:** {ctx.guild.afk_channel}\n'
                              f'**Text channels:** {len(ctx.guild.text_channels)} | '
                              f'**Voice channels:** {len(ctx.guild.voice_channels)}\n'
                              f'**Voice region:** {self.bot.utils.guild_region(ctx.guild)}\n', inline=False)

        embed.set_thumbnail(url=self.bot.utils.guild_icon(ctx.guild))
        embed.set_image(url=self.bot.utils.guild_banner(ctx.guild))
        embed.set_footer(text=f'ID: {ctx.guild.id}')

        return await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user'])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """
        Get information about you, or a specified user.

        `member`: The member who you want the information of. Can be a Mention, Name or ID
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(
            colour=self.bot.utils.member_colour(ctx.author),
            title=f"{member.name}'s Stats and Information."
        )
        embed.set_footer(text=f'ID: {member.id}')
        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        embed.add_field(name='__**General information:**__', value=f'**Discord Name:** {member}\n'
                                                                   f'**Account created:** {datetime.strftime(member.created_at, "%A %d %B %Y at %H:%M")}\n'
                                                                   f'**Status:** {self.bot.utils.member_status(member)}\n'
                                                                   f'**Activity:** {self.bot.utils.member_activity(member)}', inline=False)

        role_count = len(member.roles) - 1
        roles = ' '.join([r.mention for r in member.roles[:-11:-1] if not r.name == '@everyone'])
        if role_count > 10:
            roles += f' ... and {role_count - 10} others'

        embed.add_field(name='__**Server-related information:**__', value=f'**Nickname:** {member.nick}\n'
                                                                          f'**Joined server:** {datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}\n'
                                                                          f'**Roles:** ({role_count}) {roles}', inline=False)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
