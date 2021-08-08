import functools
import random

import discord
from discord.ext import commands

from core import colours, emojis
from core.bot import Life
from utilities import context, converters, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Economy(bot=bot))


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    # Events

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        if await self.bot.redis.exists(f"{message.author.id}_xp_gain") is True:
            return

        user_config = await self.bot.user_manager.get_config(message.author.id)

        xp = random.randint(10, 25)

        if xp >= user_config.next_level_xp:

            if not user_config.notifications.level_ups:
                return

            await message.reply(f"You are now level `{user_config.level}`!")

        user_config.change_xp(xp)
        await self.bot.redis.setex(name=f"{message.author.id}_xp_gain", time=60, value="")

    #

    @commands.command(name="level", aliases=["xp", "score", "rank"], ignore_extra=False)
    async def level(self, ctx: context.Context, person: converters.PersonConverter = utils.MISSING) -> None:
        """
        Displays yours, or another persons xp, rank, and level information.

        **person**: The person to get level information for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        user = person or ctx.author

        async with ctx.typing():
            file = await self.bot.user_manager.create_level_card(user.id, guild_id=getattr(ctx.guild, "id", None))
            await ctx.reply(file=file)

    @commands.group(name="leaderboard", aliases=["lb"], invoke_without_command=True)
    async def leaderboard(self, ctx: context.Context) -> None:
        """
        Displays the leaderboard for ranks, xp and levels.
        """

        leaderboards = (len(self.bot.user_manager.leaderboard(guild_id=getattr(ctx.guild, "id", None))) // 10) + 1

        await ctx.paginate_file(
                entries=[functools.partial(self.bot.user_manager.create_leaderboard, guild_id=getattr(ctx.guild, "id", None)) for _ in range(leaderboards)]
        )

    @leaderboard.command(name="text")
    async def leaderboard_text(self, ctx: context.Context) -> None:
        """
        Displays the leaderboard in a text table.
        """

        if not (leaderboard := self.bot.user_manager.leaderboard(guild_id=getattr(ctx.guild, "id", None))):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="There are no leaderboard stats.")

        user_config = await self.bot.user_manager.get_config(ctx.author.id)

        entries = [
            f"║ {index + 1:<5} ║ {user_config.xp:<9} ║ {user_config.level:<5} ║ {utils.name(person=self.bot.get_user(user_config.id), guild=ctx.guild):<37} ║"
            for index, user_config in enumerate(leaderboard)
        ]

        await ctx.paginate(
                entries=entries,
                per_page=10,
                header="╔═══════╦═══════════╦═══════╦═══════════════════════════════════════╗\n"
                       "║ Rank  ║ XP        ║ Level ║ Name                                  ║\n"
                       "╠═══════╬═══════════╬═══════╬═══════════════════════════════════════╣\n",
                footer=f"\n"
                       f"║       ║           ║       ║                                       ║\n"
                       f"╠═══════╬═══════════╬═══════╬═══════════════════════════════════════╣\n"
                       f"║ {self.bot.user_manager.rank(ctx.author.id, guild_id=getattr(ctx.guild, 'id', None)):<5} ║ {user_config.xp:<9} ║ {user_config.level:<5} ║ {str(ctx.author):<37} ║\n"
                       f"╚═══════╩═══════════╩═══════╩═══════════════════════════════════════╝\n",
                codeblock=True
        )
