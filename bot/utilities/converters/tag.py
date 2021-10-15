# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
from discord.ext import commands

# My stuff
from core import colours
from utilities import custom, exceptions, objects


class TagConverter(commands.Converter[objects.Tag]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.Tag:

        try:
            name = await TagNameConverter().convert(ctx=ctx, argument=argument)
        except Exception:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="That was not a valid tag name."
            )

        guild_config = await ctx.bot.guild_manager.get_config(ctx.guild.id)

        if not (tag := guild_config.get_tag(tag_name=name)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"There are no tags with the name **{name}**."
            )

        return tag


class TagNameConverter(commands.Converter[str]):

    async def convert(self, ctx: custom.Context, argument: str) -> str:

        if not (argument := (await commands.clean_content(escape_markdown=True).convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        command: Any = ctx.bot.get_command("tag")

        if argument.split(" ")[0] in (names := command.all_commands.keys()):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"Tag names can not start with a tag subcommand name. ({', '.join(f'**{name}**' for name in names)})",
            )
        if len(argument) < 3 or len(argument) > 50:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="Tag names must be between 3 and 50 characters long."
            )

        return argument


class TagContentConverter(commands.Converter[str]):

    async def convert(self, ctx: custom.Context, argument: str) -> str:

        if not (argument := (await commands.clean_content(escape_markdown=True).convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if len(argument) > 1800:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="Tag content can not be more than 1800 characters long."
            )

        return argument
