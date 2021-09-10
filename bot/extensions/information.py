# Future
from __future__ import annotations

# Standard Library
import collections
import inspect
import os
import platform
import re
import subprocess
import time
from typing import Any, Optional

# Packages
import discord
import humanize
import pkg_resources
import psutil
from discord.ext import commands

# My stuff
from core import colours, emojis, values
from core.bot import Life
from utilities import context, converters, exceptions, utils


COLOURS: dict[discord.Status, int] = {
    discord.Status.online:    0x008000,
    discord.Status.idle:      0xFF8000,
    discord.Status.dnd:       0xFF0000,
    discord.Status.offline:   0x808080,
    discord.Status.invisible: 0x808080,
}

VERIFICATION_LEVELS: dict[discord.VerificationLevel, str] = {
    discord.VerificationLevel.none:    "None - No criteria set.",
    discord.VerificationLevel.low:     "Low - Must have a verified email.",
    discord.VerificationLevel.medium:  "Medium - Must have a verified email and be registered on discord for more than 5 minutes.",
    discord.VerificationLevel.high:    "High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the server for "
                                       "more than 10 minutes.",
    discord.VerificationLevel.highest: "Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the server for "
                                       "more than 10 minutes, and have a "
                                       "verified phone number.",
}

CONTENT_FILTER_LEVELS: dict[discord.ContentFilter, str] = {
    discord.ContentFilter.disabled:    "None",
    discord.ContentFilter.no_role:     "No roles",
    discord.ContentFilter.all_members: "All members",
}

MFA_LEVELS: dict[int, str] = {
    0: "No",
    1: "Yes"
}

NSFW_LEVELS: dict[discord.NSFWLevel, str] = {
    discord.NSFWLevel.default:        "Uncategorized",
    discord.NSFWLevel.explicit:       "Explicit - Contains NSFW content.",
    discord.NSFWLevel.safe:           "Safe - No NSFW content.",
    discord.NSFWLevel.age_restricted: "Maybe - May contain NSFW content.",
}


class RoleCountOptions(commands.FlagConverter, delimiter=" ", prefix="--", case_insensitive=True):
    sorted: bool = False


def setup(bot: Life) -> None:
    bot.add_cog(Information(bot=bot))


class Information(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="serverinfo", aliases=["server-info", "server_info", "server", "guildinfo", "guild-info", "guild_info", "guild"])
    async def server_info(self, ctx: context.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays information about the current server.

        **server**: The server to get the information for, can be its Name or ID.
        """

        guild = server or ctx.guild

        status_counts: collections.Counter[Any] = collections.Counter([member.status for member in guild.members])
        status_counts[discord.Streaming] = len([m for m in guild.members if discord.utils.find(lambda a: isinstance(a, discord.Streaming), m.activities)])

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Information for **{guild.name}**:",
            description=f"**Owner:** {guild.owner} {emojis.OWNER}\n"
                        f"**Created on:** {utils.format_datetime(guild.created_at)}\n"
                        f"**Created:** {utils.format_difference(guild.created_at)} ago\n"
                        f"**Members:** {guild.member_count} | {emojis.ONLINE}{status_counts[discord.Status.online]} | "
                        f"{emojis.IDLE}{status_counts[discord.Status.idle]} | {emojis.DND}{status_counts[discord.Status.dnd]} | "
                        f"{emojis.OFFLINE}{status_counts[discord.Status.offline]} | {emojis.STREAMING}{status_counts[discord.Streaming]}\n"
                        f"**Verification level:** {VERIFICATION_LEVELS[guild.verification_level]}\n"
                        f"**Content filter level:** {CONTENT_FILTER_LEVELS[guild.explicit_content_filter]}\n"
                        f"**NSFW level:** {NSFW_LEVELS[guild.nsfw_level]}\n"
                        f"**2FA required:** {MFA_LEVELS[guild.mfa_level]}\n"
                        f"**Nitro tier:** {guild.premium_tier} | **Boosters:** {guild.premium_subscription_count}\n"
                        f"**Max file size:** {humanize.naturalsize(guild.filesize_limit)} | "
                        f"**Max bitrate:** {humanize.naturalsize(guild.bitrate_limit)}\n"
                        f"**Max emoji:** {guild.emoji_limit} | **Max video channel users:** {guild.max_video_channel_users}\n"
                        f"**AFK channel:** {guild.afk_channel.mention if guild.afk_channel else 'Not set'} | "
                        f"**AFK timeout:** {int(ctx.guild.afk_timeout / 60)}m\n"
                        f"**Rules channel:** {guild.rules_channel.mention if guild.rules_channel else 'Not set'}\n"
                        f"**Updates channel:** {guild.public_updates_channel.mention if guild.public_updates_channel else 'Not set'}\n"
                        f"**System channel:** {guild.system_channel.mention if guild.system_channel else 'Not set'}\n"
                        f"**Preferred locale:** {guild.preferred_locale or 'Not set'}",
        ).set_footer(
            text=f"ID: {guild.id} | Owner ID: {guild.owner.id}"
        ).set_thumbnail(
            url=utils.icon(guild)
        )
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="roleinfo", aliases=["role-info", "role_info", "role"])
    async def role_info(self, ctx: context.Context, *, role: discord.Role = utils.MISSING) -> None:
        """
        Displays information about the given role.

        **role**: The role to get information for. Can be its ID, Name or @Mention. Defaults to your top role in the current server.
        """

        role = role or ctx.author.top_role

        embed = discord.Embed(
            colour=role.colour,
            title=f"Information about role **{role}**:",
            description=f"**Name:** {role.name}\n"
                        f"**Created on:** {utils.format_datetime(role.created_at)}\n"
                        f"**Created:** {utils.format_difference(role.created_at)} ago\n"
                        f"**Hoisted:** {str(role.hoist).replace('True', 'Yes').replace('False', 'No')}\n"
                        f"**Managed:** {str(role.managed).replace('True', 'Yes').replace('False', 'No')}\n"
                        f"**Mentionable:** {str(role.mentionable).replace('True', 'Yes').replace('False', 'No')}\n"
                        f"**Position (from bottom):** {role.position}\n"
                        f"**Colour:** {str(role.colour).upper()}\n"
                        f"**Role members:** {len(role.members)}\n",
        ).set_footer(
            text=f"ID: {role.id}"
        )
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="icon", aliases=["ico"])
    async def icon(self, ctx: context.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays the current servers icon.

        **server**: The server to get the icon for, can be its Name or ID.
        """

        guild = server or ctx.guild

        if not guild.icon:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"The server **{guild.name}** does not have an icon."
            )

        description = f"[PNG]({utils.icon(guild, format='png')}) | [JPG]({utils.icon(guild, format='jpg')}) | [WEBP]({utils.icon(guild, format='webp')}) "
        if guild.icon.is_animated():
            description += f" | [GIF]({utils.icon(guild, format='gif')})"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Icon for **{guild.name}**:",
            description=description
        ).set_image(
            url=utils.icon(guild)
        )
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="banner")
    async def banner(self, ctx: context.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays the current servers banner.

        **server**: The server to get the banner for, can be its Name or ID.
        """

        guild = server or ctx.guild

        if not guild.banner:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"The server **{guild.name}** does not have a banner."
            )

        description = f"[PNG]({utils.banner(guild, format='png')}) | [JPG]({utils.banner(guild, format='jpg')}) | [WEBP]({utils.banner(guild, format='webp')}) "
        if guild.banner.is_animated():
            description += f" | [GIF]({utils.banner(guild, format='gif')})"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Banner for **{guild.name}**:",
            description=description
        ).set_image(
            url=utils.banner(guild)
        )
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="splash")
    async def splash(self, ctx: context.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays the current servers invite splash screen.

        **server**: The server to get the splash screen for, can be its Name or ID.
        """

        guild = server or ctx.guild

        if not guild.splash:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"The server **{guild.name}** does not have a splash."
            )

        description = f"[PNG]({utils.splash(guild, format='png')}) | [JPG]({utils.splash(guild, format='jpg')}) | [WEBP]({utils.splash(guild, format='webp')}) "
        if guild.splash.is_animated():
            description += f" | [GIF]({utils.splash(guild, format='gif')})"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Invite splash for **{guild.name}**:",
            description=description
        ).set_image(
            url=utils.splash(guild)
        )
        await ctx.reply(embed=embed)

    @commands.command(name="rolecounts", aliases=["role-counts", "role_counts", "roles", "rcs"])
    async def role_counts(self, ctx: context.Context, server: discord.Guild = utils.MISSING, *, options: RoleCountOptions) -> None:
        """
        Displays roles and how many people have them within a server.

        **server**: The server to get the information for, can be its Name or ID.
        """

        guild = server or ctx.guild

        counts = {role.name: len(role.members) for role in guild.roles}
        if options.sorted:
            counts = dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

        await ctx.paginate(
            entries=[f"{role_name[:20] + (role_name[20:] and '..'):23} | {role_count}" for role_name, role_count in counts.items()],
            per_page=20,
            codeblock=True,
        )

    @commands.command(name="channels")
    async def channels(self, ctx: context.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays a list of channels in a server.

        **guild**: The server of which to display channels for. Can be its ID or Name. Defaults to the current server.
        """

        guild = server or ctx.guild

        channels = [channel for channel in guild.channels if not isinstance(channel, discord.CategoryChannel) and not channel.category]
        categories = [category for category in guild.channels if isinstance(category, discord.CategoryChannel)]

        entries = [f"{utils.channel_emoji(c, guild=guild, member=ctx.author)}{c}" for c in sorted(channels, key=lambda channel: channel.position)]

        space = "\u200b " * 5
        for category in sorted(categories, key=lambda category: category.position):
            entries.append(f"{emojis.CHANNELS['CATEGORY']} **{category}**")
            for channel in category.channels:
                entries.append(f"{space}{utils.channel_emoji(channel, guild=guild, member=ctx.author)}{channel}")

        await ctx.paginate_embed(
            entries=entries,
            per_page=30,
            title=f"Channels in **{guild}**:"
        )

    #

    @commands.command(name="userinfo", aliases=["user-info", "user_info", "user", "memberinfo", "member-info", "member_info", "member"])
    async def user_info(self, ctx: context.Context, *, person: converters.PersonConverter = utils.MISSING) -> None:
        """
        Displays information about the given person.

        **person**: The person to get information for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        user = person or ctx.author

        description = f"**Created on:** {utils.format_datetime(user.created_at)}\n" \
                      f"**Created:** {utils.format_difference(user.created_at)} ago\n" \
                      f"**Badges:** {utils.badge_emojis(user)}\n" \
                      f"**Bot account:** {str(user.bot).replace('True', 'Yes').replace('False', 'No')}\n" \
                      f"**System account:** {str(user.system).replace('True', 'Yes').replace('False', 'No')}\n" \
                      f"**Mutual guilds:** {len(user.mutual_guilds)}\n"

        if isinstance(user, discord.Member):
            description += f"**Status:** {user.status.name.replace('dnd', 'Do Not Disturb').title()}{emojis.PHONE if user.is_on_mobile() else ''}\n" \
                           f"**Activity:**\n{utils.activities(user)}\n"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Information about **{user}**:",
            description=description
        ).set_footer(
            text=f"ID: {user.id}"
        ).set_thumbnail(
            url=utils.avatar(user)
        )

        if isinstance(user, discord.Member):
            embed.add_field(
                name="Server related information:",
                value=f"**Nickname:** {user.nick}\n"
                      f"**Joined on:** {utils.format_datetime(user.joined_at)}\n"
                      f"**Joined:** {utils.format_difference(user.joined_at)} ago\n"
                      f"**Join Position:** {sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1}\n"
                      f"**Top role:** {user.top_role.mention}\n"
                      f"**Role count:** {len(user.roles) - 1}\n",
            )

        await ctx.reply(embed=embed)

    @commands.command(name="avatar", aliases=["avy"])
    async def avatar(self, ctx: context.Context, *, person: converters.PersonConverter = utils.MISSING) -> None:
        """
        Display a persons avatar.

        **person**: The person to get the avatar of. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        user = person or ctx.author

        description = f"[PNG]({utils.avatar(user, format='png')}) | [JPG]({utils.avatar(user, format='jpg')}) | [WEBP]({utils.avatar(user, format='webp')}) "
        if user.avatar.is_animated():
            description += f" | [GIF]({utils.avatar(user, format='gif')})"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Avatar for **{user}**:",
            description=description
        ).set_image(
            url=utils.avatar(user)
        )
        await ctx.reply(embed=embed)

    #

    @commands.command(name="ping")
    async def ping(self, ctx: context.Context) -> None:
        """
        Displays the bots various pings.
        """

        typing_start = time.perf_counter()
        await ctx.trigger_typing()
        typing_end = time.perf_counter()

        db_start = time.perf_counter()
        await self.bot.db.fetch("SELECT 1")
        db_end = time.perf_counter()

        redis_start = time.perf_counter()
        await self.bot.redis.set("ping", "value")
        redis_end = time.perf_counter()

        embed = discord.Embed(
            colour=colours.MAIN,
            title="Ping:",
        ).add_field(
            name="Websocket:",
            value=f"```py\n{self.bot.latency * 1000:.2f} ms\n```"
        ).add_field(
            name="API:",
            value=f"```py\n{(typing_end - typing_start) * 1000:.2f} ms\n```"
        ).add_field(
            name="\u200B",
            value="\u200B"
        ).add_field(
            name="PSQL:",
            value=f"```py\n{(db_end - db_start) * 1000:.2f} ms\n```"
        ).add_field(
            name="Redis:",
            value=f"```py\n{(redis_end - redis_start) * 1000:.2f} ms\n```"
        ).add_field(
            name="\u200B",
            value="\u200B"
        )

        await ctx.reply(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx: context.Context) -> None:
        """
        Display the bots stats.
        """

        embed = discord.Embed(
            colour=colours.MAIN,
            title="Stats:",
            description=f"`Uptime:` {utils.format_seconds(time.time() - self.bot.start_time, friendly=True)}\n"
                        f"`Shards:` {len(self.bot.shards)}\n"
                        f"`Servers:` {len(self.bot.guilds)}\n"
                        f"`Members:` {sum(len(guild.members) for guild in self.bot.guilds)}\n"
                        f"`Users:` {len(self.bot.users)}\n"
                        f"`Extensions:` {len(self.bot.extensions)}\n"
                        f"`Cogs:` {len(self.bot.cogs)}\n"
                        f"`Commands:` {len(self.bot.commands)}\n\n"
                        f"**Version Info:**\n"
                        f"`discord.py:` {pkg_resources.get_distribution('discord.py').version}\n"
                        f"`asyncpg:` {pkg_resources.get_distribution('asyncpg').version}\n"
                        f"`aioredis:` {pkg_resources.get_distribution('aioredis').version}\n"
                        f"`aiohttp:` {pkg_resources.get_distribution('aiohttp').version}\n"
                        f"`slate:` {pkg_resources.get_distribution('slate').version}\n"
                        f"`pillow:` {pkg_resources.get_distribution('pillow').version}\n"
                        f"`wand:` {pkg_resources.get_distribution('wand').version}\n",
        )
        await ctx.reply(embed=embed)

    @commands.command(name="system", aliases=["sys"])
    async def system(self, ctx: context.Context) -> None:
        """
        Display the bot"s system stats.
        """

        cpu_freq: Any = psutil.cpu_freq()
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")

        java_version = re.search(r'\"(\d+\.\d+).*\"', subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT).decode()).groups()[0]

        embed = discord.Embed(
            colour=colours.MAIN,
            title="System stats:",
            description=f"`OS:` {platform.platform()}\n"
                        f"`Python version:` {platform.python_version()} ({platform.python_implementation()})\n"
                        f"`Java version:` {java_version}\n"
                        f"`Uptime:` {utils.format_seconds(time.time() - self.bot.start_time, friendly=True)}\n",
        ).add_field(
            name="System CPU:",
            value=f"`Frequency:` {round(cpu_freq.current, 2)} Mhz\n"
                  f"`Cores (logical):` {psutil.cpu_count()}\n"
                  f"`Overall Usage:` {psutil.cpu_percent(interval=0.1)}%",
        ).add_field(
            name="\u200B", value="\u200B"
        ).add_field(
            name="System Memory:",
            value=f"`Available:` {humanize.naturalsize(memory_info.available, binary=True)}\n"
                  f"`Total:` {humanize.naturalsize(memory_info.total, binary=True)}\n"
                  f"`Used:` {humanize.naturalsize(memory_info.used, binary=True)}",
        ).add_field(
            name="System Disk:",
            value=f"`Total:` {humanize.naturalsize(disk_usage.total, binary=True)}\n"
                  f"`Used:` {humanize.naturalsize(disk_usage.used, binary=True)}\n"
                  f"`Free:` {humanize.naturalsize(disk_usage.free, binary=True)}",
        ).add_field(
            name="\u200B", value="\u200B"
        ).add_field(
            name="Process information:",
            value=f"`Memory usage:` {humanize.naturalsize(self.bot.process.memory_full_info().rss, binary=True)}\n"
                  f"`CPU usage:` {self.bot.process.cpu_percent()} %\n"
                  f"`Threads:` {self.bot.process.num_threads()}",
        )

        await ctx.reply(embed=embed)

    @commands.command(name="source", aliases=["src"])
    async def source(self, ctx: context.Context, *, command: Optional[str]) -> None:

        if not command:
            await ctx.reply(
                embed=utils.embed(
                    emoji="\U0001f4da",
                    description=f"My source code can be viewed here: **{values.GITHUB_LINK}**"
                )
            )
            return

        if command == "help":
            source = type(self.bot.help_command)
            module = source.__module__
            filename: str = str(inspect.getsourcefile(source))

        else:
            if (obj := self.bot.get_command(command.replace(".", ""))) is None:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="I couldn't find that command."
                )

            source = obj.callback.__code__
            module = obj.callback.__module__
            filename = source.co_filename

        lines, start_line_number = inspect.getsourcelines(source)

        if not module.startswith("discord"):
            location = os.path.relpath(filename).replace("\\", "/")
            await ctx.reply(f"{values.GITHUB_LINK}/blob/main/bot/{location}#L{start_line_number}-L{start_line_number + len(lines) - 1}>")
        else:
            location = module.replace(".", "/") + ".py"
            await ctx.reply(f"<https://github.com/Rapptz/discord.py/blob/master/{location}#L{start_line_number}-L{start_line_number + len(lines) - 1}>")
