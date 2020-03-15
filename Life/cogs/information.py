import inspect
import os

import discord
import psutil
from discord.ext import commands

from cogs.utilities import utils


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", aliases=["info"])
    async def about(self, ctx):
        """
        Get information about the bot.
        """

        latency_ms, average_latency_ms, typing_ms, discord_ms = await utils.ping(self.bot, ctx)
        files, functions, comments, lines, classes = utils.linecount()

        embed = discord.Embed(
            colour=discord.Color.gold(),
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format="png"), name=f"{self.bot.user.name}'s Info")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        embed.set_footer(text=f"ID: {self.bot.user.id}")
        embed.description = "Life is a discord bot coded by <@238356301439041536>"
        embed.add_field(name="__**Bot info:**__", value=f"**Uptime:** {utils.format_time(self.bot.uptime)}\n"
                                                        f"**Total users:** {len(self.bot.users)}\n"
                                                        f"**Guilds:** {len(self.bot.guilds)}")
        embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(name="__**Stats:**__", value=f"**Discord.py Version:** {str(discord.__version__)}\n"
                                                     f"**Commands:** {len(self.bot.commands)}\n"
                                                     f"**Cogs:** {len(self.bot.cogs)}")
        embed.add_field(name="__**Code:**__", value=f"**Comments:** {comments}\n**Functions:** {functions}\n"
                                                    f"**Classes:** {classes}\n**Lines:** {lines}\n**Files:** {files}\n")
        embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(name="__**Ping:**__", value=f"**Average Lat:** {average_latency_ms}\n**Latency:** {latency_ms}\n"
                                                    f"**Typing:** {typing_ms}\n**Discord:** {discord_ms}")
        embed.add_field(name="__**Links:**__", value=f"**[Bot Invite](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=103926848)** | "
                                                     f"**[Support server](https://discord.gg/xP8xsHr)** | "
                                                     f"**[Source code](https://github.com/iDevision/Life)**", inline=False)
        return await ctx.send(embed=embed)

    @commands.command(name="system", aliases=["sys"])
    async def system(self, ctx):
        """
        Get information about the system the bot is running on.
        """

        embed = discord.Embed(
            colour=discord.Color.gold(),
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format="png"), name=f"{self.bot.user.name}'s system stats")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        embed.add_field(name="__**System CPU:**__", value=f"**Cores:** {psutil.cpu_count()}\n"
                                                          f"**Usage:** {psutil.cpu_percent(interval=0.1)}%\n"
                                                          f"**Frequency:** {round(psutil.cpu_freq().current, 2)} Mhz")
        embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(name="__**System Memory:**__", value=f"**Total:** {round(psutil.virtual_memory().total / 1048576)} mb\n"
                                                             f"**Used:** {round(psutil.virtual_memory().used / 1048576)} mb\n"
                                                             f"**Available:** {round(psutil.virtual_memory().available / 1048576)} mb")
        embed.add_field(name="__**System Disk:**__", value=f"**Total:** {round(psutil.disk_usage('/').total / 1073741824, 2)} GB\n"
                                                           f"**Used:** {round(psutil.disk_usage('/').used / 1073741824, 2)} GB\n"
                                                           f"**Free:** {round(psutil.disk_usage('/').free / 1073741824, 2)} GB")
        embed.add_field(name="\u200B", value="\u200B")
        embed.add_field(name="__**Process information:**__", value=f"**Memory usage:** {round(self.bot.process.memory_full_info().rss / 1048576, 2)} mb\n"
                                                                   f"**CPU usage:** {self.bot.process.cpu_percent()}%\n"
                                                                   f"**Threads:** {self.bot.process.num_threads()}")
        return await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Gets the bots ping.
        """

        latency_ms, average_latency_ms, typing_ms, discord_ms = await utils.ping(self.bot, ctx)
        return await ctx.send(f"```py\n"
                              f"Type         |Ping\n"
                              f"Average Lat. |{average_latency_ms}\n"
                              f"Latency      |{latency_ms}\n"
                              f"Typing       |{typing_ms}\n"
                              f"Discord      |{discord_ms}\n"
                              f"```")

    @commands.command(name="source")
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link to the source of a command.

        `command`: The name of the command you want the source for.
        """

        if command is None:
            return await ctx.send(f"<https://github.com/iDevision/Life>")
        obj = self.bot.get_command(command.replace(".", " "))
        if obj is None:
            return await ctx.send("I could not find that command.")
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        location = ""
        if not obj.callback.__module__.startswith("discord"):
            location = os.path.relpath(src.co_filename).replace("\\", "/")
        return await ctx.send(f"<https://github.com/iDevision/Life/blob/master/Life/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>")

    @commands.command(name="avatar")
    async def avatar(self, ctx, *, member: discord.Member = None):
        """
        Get yours or a specified members avatar.

        `member`: The member who you want the avatar of. Can be a Mention, Name or ID
        """

        if not member:
            member = ctx.author

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"{member.name}'s Avatar",
            description=f"[PNG]({member.avatar_url_as(size=1024, format='png')}) | " 
                        f"[JPEG]({member.avatar_url_as(size=1024, format='jpeg')}) | "
                        f"[WEBP]({member.avatar_url_as(size=1024, format='webp')})"
        )
        embed.set_author(icon_url=ctx.author.avatar_url_as(format="png"), name=ctx.author.name)

        if member.is_avatar_animated():
            embed.description += f" | [GIF]({member.avatar_url_as(size=1024, format='gif')})"
            embed.set_image(url=f"{member.avatar_url_as(size=1024, format='gif')}")
        else:
            embed.set_image(url=f"{member.avatar_url_as(size=1024, format='png')}")

        return await ctx.send(embed=embed)

    @commands.command(name="serverinfo", aliases=["guildinfo"])
    async def serverinfo(self, ctx):
        """
        Get information about the current server.
        """

        online, idle, dnd, offline = utils.guild_user_status(ctx.guild)

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"{ctx.guild.name}'s Stats and Information."
        )
        embed.set_author(icon_url=ctx.author.avatar_url_as(format="png"), name=ctx.author.name)
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png", size=1024))
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        embed.add_field(name="__**General information:**__", value=f"**Owner:** {ctx.guild.owner}\n"
                                                                   f"**Server created at:** {ctx.guild.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                   f"**Members:** {ctx.guild.member_count} |"
                                                                   f"<:online:627627415224713226>{online} |"
                                                                   f"<:away:627627415119724554>{idle} |"
                                                                   f"<:dnd:627627404784828416>{dnd} |"
                                                                   f"<:offline:627627415144890389>{offline}\n"
                                                                   f"**Verification level:** {utils.guild_verification_level(ctx.guild)}\n"
                                                                   f"**Content filter level:** {utils.guild_content_filter_level(ctx.guild)}\n"
                                                                   f"**2FA:** {utils.guild_mfa_level(ctx.guild)}\n", inline=False)
        embed.add_field(name="__**Channels:**__", value=f"**Text channels:** {len(ctx.guild.text_channels)}\n"
                                                        f"**Voice channels:** {len(ctx.guild.voice_channels)}\n"
                                                        f"**Voice region:** {utils.guild_region(ctx.guild)}\n"
                                                        f"**AFK timeout:** {int(ctx.guild.afk_timeout / 60)} minutes\n"
                                                        f"**AFK channel:** {ctx.guild.afk_channel}\n", inline=False)

        roles = ' '.join([r.mention for r in ctx.guild.roles[:-11:-1] if not r.name == "@everyone"])
        role_count = len(ctx.guild.roles) - 1
        if role_count > 10:
            roles += f" ... and {role_count - 10} others"
        embed.add_field(name="__**Role information:**__", value=f"**Roles:** ({role_count}) {roles}\n", inline=False)

        return await ctx.send(embed=embed)

    @commands.command(name="userinfo", aliases=["user"])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """
        Get information about you, or a specified user.

        `member`: The member who you want the information of. Can be a Mention, Name or ID
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(
            colour=utils.member_colour(ctx.author),
            title=f"{member.name}'s Stats and Information."
        )
        embed.set_author(icon_url=ctx.author.avatar_url_as(format="png"), name=ctx.author.name)
        embed.set_footer(text=f"ID: {member.id}")
        embed.set_thumbnail(url=member.avatar_url_as(format="png"))
        embed.add_field(name="__**General information:**__", value=f"**Discord Name:** {member}\n"
                                                                   f"**Account created:** {member.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                   f"**Status:** {utils.member_status(member)}\n"
                                                                   f"**Activity:** {utils.member_activity(member)}", inline=False)

        roles = ' '.join([r.mention for r in member.roles[:-11:-1] if not r.name == "@everyone"])
        role_count = len(member.roles) - 1
        if role_count > 10:
            roles += f" ... and {role_count - 10} others"

        embed.add_field(name="__**Server-related information:**__", value=f"**Nickname:** {member.nick}\n"
                                                                          f"**Joined server:** {member.joined_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                          f"**Roles:** ({role_count}) {roles}", inline=False)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
