# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
from discord.ext import commands

# My stuff
from core import colours, emojis
from core.bot import Life
from utilities import checks, context, enums, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Settings(bot=bot))


class Settings(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name="embedsize", aliases=["embed-size", "embed_size", "es"])
    async def embed_size(
        self,
        ctx: context.Context,
        operation: Literal["set", "reset"] = utils.MISSING,
        size: Literal["large", "medium", "small"] = utils.MISSING
    ) -> None:
        """
        Manage this servers embed size settings.

        **operation**: The operation to perform, can be **set** or **reset**.
        **size**: The size to set embeds too. Can be **large**, **medium** or **small**.
        """

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not operation:
            embed = utils.embed(
                description=f"The embed size is **{guild_config.embed_size.name.title()}**."
            )
            await ctx.reply(embed=embed)
            return

        try:
            await checks.is_mod().predicate(ctx=ctx)
        except commands.CheckAnyFailure:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"You do not have permission to edit the bots embed size in this server."
            )

        if operation == "set":

            if not size:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"You didn't provide an embed size."
                )

            embed_size = getattr(enums.EmbedSize, size.upper(), None)

            if guild_config.embed_size is embed_size:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"The embed size is already **{embed_size.name.title()}**."
                )

            await guild_config.set_embed_size(embed_size)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Set the embed size to **{embed_size.name.title()}**."
            )
            await ctx.reply(embed=embed)

        elif operation == "reset":

            if guild_config.embed_size is enums.EmbedSize.MEDIUM:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"The embed size is already the default of **Medium**."
                )

            await guild_config.set_embed_size(enums.EmbedSize.MEDIUM)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Reset the embed size to **Medium**."
            )
            await ctx.reply(embed=embed)

    @commands.command(name="prefixes", aliases=["prefix"])
    async def prefixes(
        self,
        ctx: context.Context,
        operation: Literal["add", "remove", "reset", "clear"] = utils.MISSING,
        prefix: str = utils.MISSING
    ) -> None:
        """
        Manage this servers prefix settings.

        **operation**: The operation to perform, can be **add**, **remove** or **reset**/**clear**.
        **prefix**: The prefix to add or remove. Must be less than 15 characters, and contain no backtick characters.
        """

        if not operation:
            prefixes = await self.bot.get_prefix(ctx.message)
            await ctx.paginate_embed(
                entries=[f"`1.` {prefixes[0]}", *[f"`{index + 2}.` `{prefix}`" for index, prefix in enumerate(prefixes[2:])]],
                per_page=10,
                title="List of usable prefixes."
            )
            return

        try:
            await checks.is_mod().predicate(ctx=ctx)
        except commands.CheckAnyFailure:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"You do not have permission to edit the bots prefixes in this server."
            )

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if operation == "add":

            if not prefix:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You didn't provide a prefix to add."
                )
            if prefix in guild_config.prefixes:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"This server already has the prefix **{prefix}**."
                )
            if len(guild_config.prefixes) > 20:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="This server can not have more than 20 custom prefixes."
                )

            await guild_config.change_prefixes(prefix=prefix, operation=enums.Operation.ADD)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Added **{prefix}** to this servers prefixes."
            )
            await ctx.reply(embed=embed)

        elif operation == "remove":

            if not prefix:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You did not provide a prefix to remove."

                )
            if prefix not in guild_config.prefixes:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"This server does not have the prefix **{prefix}**."
                )

            await guild_config.change_prefixes(prefix=prefix, operation=enums.Operation.REMOVE)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Remove **{prefix}** from this servers prefixes."
            )
            await ctx.reply(embed=embed)

        elif operation in {"reset", "clear"}:

            if not guild_config.prefixes:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="This server does not have any custom prefixes."
                )

            await guild_config.change_prefixes(operation=enums.Operation.RESET)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Cleared this servers prefixes."
            )
            await ctx.reply(embed=embed)
