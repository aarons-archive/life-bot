# Future
from __future__ import annotations

# Standard Library
import collections
import time

# Packages
from discord.ext import commands

# My stuff
from core import colours, config, emojis
from core.bot import Life
from utilities import context, converters, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Dev(bot=bot))


class Dev(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.group(name="dev", hidden=True, invoke_without_command=True)
    async def dev(self, ctx: context.Context[Life]) -> None:
        """
        Base command for bot developer commands.
        """

        await ctx.invoke(self.bot.get_command("jsk"))

    @commands.is_owner()
    @dev.command(name="cleanup", aliases=["clean"], hidden=True)
    async def dev_cleanup(self, ctx: context.Context[Life], limit: int = 100) -> None:
        """
        Deletes the bots messages.

        **limit**: The amount of messages to check back through to delete.
        """

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me or message.content.startswith(config.PREFIX),
                limit=limit
            )
        else:
            messages = await ctx.channel.purge(
                check=lambda message: message.author == ctx.me,
                bulk=False,
                limit=limit
            )

        s = "s" if len(messages) > 1 else ""
        s1 = "s" if limit > 1 else ""  # TODO: Pluraliser or something??

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Found and deleted **{len(messages)}** message{s} out of the last **{limit}** message{s1}.",
        )
        await ctx.reply(embed=embed, delete_after=10)

    @commands.is_owner()
    @dev.command(name="guilds", aliases=["g", "servers", "s"], hidden=True)
    async def dev_guilds(self, ctx: context.Context[Life]) -> None:
        """
        Displays a list of servers the bot is in.
        """

        entries = []
        sorted_guilds = sorted(
            self.bot.guilds,
            reverse=True,
            key=lambda _guild: sum(bool(member.bot) for member in _guild.members) / len(_guild.members) * 100,
        )

        for guild in sorted_guilds:

            total = len(guild.members)
            members = sum(not m.bot for m in guild.members)
            bots = sum(1 for m in guild.members if m.bot)
            percent_bots = f"{round((bots / total) * 100, 2)}%"

            entries.append(f"║ {guild.id:<19} ║ {total:<8} ║ {members:<8} ║ {bots:<8} ║ {percent_bots:8} ║ {guild.name}")

        await ctx.paginate(
            entries=entries,
            per_page=20,
            header="╔═════════════════════╦══════════╦══════════╦══════════╦══════════╦═════════════════════\n"
                   "║ Guild id            ║ Total    ║ Members  ║ Bots     ║ Percent  ║ Name\n"
                   "╠═════════════════════╬══════════╬══════════╬══════════╬══════════╬═════════════════════\n",
            footer="\n"
                   "╚═════════════════════╩══════════╩══════════╩══════════╩══════════╩═════════════════════",
            codeblock=True
        )

    @commands.is_owner()
    @dev.command(name="socketstats", aliases=["ss"], hidden=True)
    async def dev_socket_stats(self, ctx: context.Context[Life]) -> None:
        """
        Displays a list of socket event counts since bot startup.
        """

        event_stats = collections.OrderedDict(sorted(self.bot.socket_stats.items(), key=lambda kv: kv[1], reverse=True))
        total = sum(event_stats.values())
        per_second = round(total / round(time.time() - self.bot.start_time))

        await ctx.paginate(
            entries=[f"║ {event:40} ║ {count:<8} ║" for event, count in event_stats.items()],
            per_page=20,
            header=f"{total} socket events observed at a rate of {per_second} per second.\n"
                   "╔══════════════════════════════════════════╦══════════╗\n"
                   "║ Event                                    ║ Count    ║\n"
                   "╠══════════════════════════════════════════╬══════════╣\n",
            footer="\n"
                   "╚══════════════════════════════════════════╩══════════╝",
            codeblock=True
        )

    @commands.is_owner()
    @commands.group(name="blacklist", aliases=["bl"], hidden=True, invoke_without_command=True)
    async def blacklist(self, ctx: context.Context[Life]) -> None:
        """
        Displays blacklisted users.
        """

        blacklisted = await self.bot.db.fetch("SELECT * FROM users WHERE blacklisted = $1", True)
        if not blacklisted:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There are no blacklisted users."
            )

        await ctx.paginate(
            entries=[f"║ {user_config['id']:<19} ║ {user_config['blacklisted_reason']:62} ║" for user_config in blacklisted],
            per_page=15,
            header="╔═════════════════════╦════════════════════════════════════════════════════════════════╗\n"
                   "║ User id             ║ Reason                                                         ║\n"
                   "╠═════════════════════╬════════════════════════════════════════════════════════════════╣\n",
            footer="\n"
                   "╚═════════════════════╩════════════════════════════════════════════════════════════════╝",
            codeblock=True
        )

    @commands.is_owner()
    @blacklist.command(name="add", hidden=True)
    async def blacklist_add(self, ctx: context.Context[Life], user: converters.PersonConverter, *, reason: str | None) -> None:
        """
        Adds a user to the blacklist.

        **user**: The user to blacklist, can be their ID, Username, Nickname or @Mention.
        **reason**: Reason why the user is being blacklisted.
        """

        reason = reason or f"{user} - No reason"

        user_config = await self.bot.user_manager.get_config(user.id)
        if user_config.blacklisted is True:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{user}** is already blacklisted."
            )

        await user_config.set_blacklisted(True, reason=reason)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Added **{user}** to the blacklist."
        )
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @blacklist.command(name="remove", hidden=True)
    async def blacklist_remove(self, ctx: context.Context[Life], user: converters.PersonConverter) -> None:
        """
        Removes a user from the blacklist.

        **user**: The user to remove from the blacklist, can be their ID, Username, Nickname or @Mention.
        """

        user_config = await self.bot.user_manager.get_config(user.id)
        if user_config.blacklisted is False:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{user}** is not blacklisted."
            )

        await user_config.set_blacklisted(False)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Removed **{user}** from the blacklist."
            )
        )
