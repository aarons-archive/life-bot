from discord.ext import commands
from .utilities import formatting
from .utilities import utils
import discord
import inspect
import psutil
import time
import os


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", aliases=["info"])
    async def about(self, ctx):
        """
        Get information about the bot.
        """

        # Get bot information.
        typingms, latencyms, discordms, average = await utils.ping(self.bot, ctx)
        files, functions, comments, lines = utils.linecount()
        uptime = time.time() - self.bot.start_time

        # Create embed
        embed = discord.Embed(
            colour=discord.Color.gold(),
        )
        embed.set_author(icon_url=self.bot.user.avatar_url_as(format="png"), name=f"{self.bot.user.name}'s Info")
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        embed.set_footer(text=f"ID: {self.bot.user.id}")
        embed.add_field(name="__**Bot info:**__", value=f"**Uptime:** {formatting.get_time_friendly(uptime)}\n"
                                                        f"**Total users:** {len(self.bot.users)}\n"
                                                        f"**Guilds:** {len(self.bot.guilds)}\n")
        embed.add_field(name="__**Stats:**__", value=f"**Discord.py Version:** {str(discord.__version__)}\n"
                                                     f"**Commands:** {len(self.bot.commands)}\n"
                                                     f"**Cogs:** {len(self.bot.cogs)}\n")
        embed.add_field(name="__**Code:**__", value=f"**Comments:** {comments}\n**Functions:** {functions}\n"
                                                    f"**Lines:** {lines}\n**Files:** {files}\n")
        embed.add_field(name="__**Ping:**__", value=f"**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n"
                                                    f"**Discord:** {discordms}ms\n**Average:** {average}ms")
        embed.add_field(name="__**Links:**__", value=f"**[Bot Invite](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot)** | "
                                                     f"**[Support server](https://discord.gg/XejxSqT)** | "
                                                     f"**[Source code](https://github.com/MyNameBeMrRandom/Life)**", inline=False)
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
        embed.add_field(name="__**System Memory:**__", value=f"**Total:** {round(psutil.virtual_memory().total/1048576)} mb\n"
                                                             f"**Used:** {round(psutil.virtual_memory().used/1048576)} mb\n"
                                                             f"**Available:** {round(psutil.virtual_memory().available/1048576)} mb")
        embed.add_field(name="__**System Disk:**__", value=f"**Total:** {round(psutil.disk_usage('/').total/1073741824, 2)} GB\n"
                                                           f"**Used:** {round(psutil.disk_usage('/').used/1073741824, 2)} GB\n"
                                                           f"**Free:** {round(psutil.disk_usage('/').free/1073741824, 2)} GB")
        embed.add_field(name="__**Process information:**__", value=f"**Memory usage:** {round(self.bot.process.memory_full_info().rss/1048576, 2)} mb\n"
                                                                   f"**CPU usage:** {self.bot.process.cpu_percent()}%\n"
                                                                   f"**Threads:** {self.bot.process.num_threads()}")
        return await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Gets the bots ping.
        """

        typingms, latencyms, discordms, average = await utils.ping(self.bot, ctx)
        return await ctx.send(f"**Typing:** {typingms}ms\n**Latency:** {latencyms}ms\n"
                              f"**Discord:** {discordms}ms\n**Average:** {average}ms")

    @commands.command(name="source")
    async def source(self, ctx, *, command: str = None):
        """
        Get a github link for the source of a command.

        `command`: The name of the command you want the source for.
        """

        github_url = "https://github.com/MyNameBeMrRandom/Life"
        if command is None:
            return await ctx.send(f"<{github_url}>")
        obj = self.bot.get_command(command.replace(".", " "))
        if obj is None:
            return await ctx.send("I could not find that command.")
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        location = ""
        if not obj.callback.__module__.startswith("discord"):
            location = os.path.relpath(src.co_filename).replace("\\", "/")
        final_url = f"<{github_url}/blob/master/Life/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

    @commands.command(name="avatar")
    async def avatar(self, ctx, *, user: discord.Member = None):
        """
        Get yours or a specified users avatar.


        `user`: The user who you want the avatar of. Can be an ID, mention or name.
        """

        # If the user didnt choose someone.
        if not user:
            user = ctx.author

        embed = discord.Embed(
            colour=discord.Color.gold(),
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if user.is_avatar_animated():
            embed.add_field(name=f"{user.name}'s Avatar", value=f"[GIF]({user.avatar_url_as(size=1024, format='gif')}) | "
                                                                f"[PNG]({user.avatar_url_as(size=1024, format='png')}) | "
                                                                f"[JPEG]({user.avatar_url_as(size=1024, format='jpeg')}) | "
                                                                f"[WEBP]({user.avatar_url_as(size=1024, format='webp')})", inline=False)
            embed.set_image(url=f"{user.avatar_url_as(size=1024, format='gif')}")
        else:
            embed.add_field(name=f"{user.name}'s Avatar", value=f"[PNG]({user.avatar_url_as(size=1024, format='png')}) | "
                                                                f"[JPEG]({user.avatar_url_as(size=1024, format='jpeg')}) | "
                                                                f"[WEBP]({user.avatar_url_as(size=1024, format='webp')})", inline=False)
            embed.set_image(url=f"{user.avatar_url_as(size=1024, format='png')}")
        return await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """
        Get information about the current server.
        """

        online, offline, idle, dnd = utils.guild_user_status_count(ctx.guild)
        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"{ctx.guild.name}'s Stats and Information."
        )
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
                                                        f"**AFK timeout:** {int(ctx.guild.afk_timeout/60)} minutes\n"
                                                        f"**AFK channel:** {ctx.guild.afk_channel}\n", inline=False)
        embed.add_field(name="__**Role information:**__", value=f"**Roles:** {' '.join([r.mention for r in ctx.guild.roles[1:]])}\n"
                                                                f"**Count:** {len(ctx.guild.roles)}\n", inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        return await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """
        Get information about you, or a specified user.

        `user`: The user who you want information about. Can be an ID, mention or name.
        """

        if not user:
            user = ctx.author
        user = ctx.guild.get_member(user.id)
        embed = discord.Embed(
            colour=utils.embed_color(user),
            title=f"{user.name}'s Stats and Information."
        )
        embed.set_footer(text=f"ID: {user.id}")
        embed.add_field(name="__**General information:**__", value=f"**Discord Name:** {user}\n"
                                                                   f"**Account created:** {user.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                   f"**Status:** {utils.user_status(user)}\n"
                                                                   f"**Activity:** {utils.user_activity(user)}", inline=False)
        embed.add_field(name="__**Server-related information:**__", value=f"**Nickname:** {user.nick}\n"
                                                                          f"**Joined server:** {user.joined_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                          f"**Roles:** {' '.join([r.mention for r in user.roles[1:]])}")
        embed.set_thumbnail(url=user.avatar_url)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
