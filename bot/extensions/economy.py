# Future
from __future__ import annotations

# Standard Library
import functools
import random

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours, emojis
from core.bot import Life
from utilities import context, converters, enums, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Economy(bot=bot))


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    # Events

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.guild is None or message.author.bot is True:
            return

        if bool(await self.bot.redis.exists(f"{message.author.id}_{message.guild.id}_xp_gain")) is True:
            return

        user_config = await self.bot.user_manager.get_config(message.author.id)
        member_config = await user_config.get_member_config(message.guild.id)

        xp = random.randint(10, 25)
        await member_config.change_xp(xp, operation=enums.Operation.ADD)

        if xp >= member_config.needed_xp and user_config.notifications.level_ups:
            await message.reply(f"You are now level `{member_config.level}`!")

        await self.bot.redis.setex(name=f"{message.author.id}_{message.guild.id}_xp_gain", time=60, value="")

    #

    @commands.command(name="level", aliases=["xp", "score", "rank"], ignore_extra=False)
    async def level(self, ctx: context.Context, person: converters.PersonConverter = utils.MISSING) -> None:
        """
        Displays yours, or another persons xp, rank, and level information.

        **person**: The person to get level information for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        user = person or ctx.author

        async with ctx.typing():
            buffer = await self.bot.user_manager.create_level_card(guild_id=ctx.guild.id, user_id=user.id)
            url = await utils.upload_file(self.bot.session, file_bytes=buffer, file_format="png")
            buffer.close()

            await ctx.reply(url)

    @commands.group(name="leaderboard", aliases=["lb"], invoke_without_command=True)
    async def leaderboard(self, ctx: context.Context) -> None:
        """
        Displays the leaderboard for ranks, xp and levels.
        """

        pages = ((await self.bot.db.fetchrow("SELECT count(*) FROM members WHERE guild_id = $1", ctx.guild.id))["count"] // 10) + 1
        await ctx.paginate_file(
            entries=[functools.partial(self.bot.user_manager.create_leaderboard, guild_id=ctx.guild.id, page=page + 1) for page in range(pages)]
        )

    @leaderboard.command(name="text")
    async def leaderboard_text(self, ctx: context.Context) -> None:
        """
        Displays the leaderboard in a text table.
        """

        leaderboard = await self.bot.user_manager.leaderboard(guild_id=ctx.guild.id, page=0, limit=None)
        if not (member_config := discord.utils.find(lambda r: r['user_id'] == ctx.author.id, leaderboard)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Something went wrong while fetching the leaderboard."
            )

        entries = []

        for record in leaderboard:

            if not (member := ctx.guild.get_member(record["user_id"])):
                continue

            entries.append(f"║ {record['rank']:<5} ║ {record['xp']:<9} ║ {utils.level(record['xp']):<5} ║ {member.nick or member.name:<37} ║")

        author_stats = f"║ {await self.bot.user_manager.rank(guild_id=ctx.guild.id, user_id=ctx.author.id):<5} ║ {member_config['xp']:<9} " \
                       f"║ {utils.level(member_config['xp']):<5} ║ {ctx.author.nick or ctx.author.name:<37} ║\n"

        await ctx.paginate(
            entries=entries,
            per_page=10,
            header="╔═══════╦═══════════╦═══════╦═══════════════════════════════════════╗\n"
                   "║ Rank  ║ XP        ║ Level ║ Name                                  ║\n"
                   "╠═══════╬═══════════╬═══════╬═══════════════════════════════════════╣\n",
            footer=f"\n"
                   f"║       ║           ║       ║                                       ║\n"
                   f"╠═══════╬═══════════╬═══════╬═══════════════════════════════════════╣\n"
                   f"{author_stats}"
                   f"╚═══════╩═══════════╩═══════╩═══════════════════════════════════════╝\n",
            codeblock=True
        )
