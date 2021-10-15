# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import custom, exceptions, objects


class TodoConverter(commands.Converter[objects.Todo]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.Todo:

        try:
            todo_id = int(argument)
        except ValueError:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="That was not a valid todo id."
            )

        user_config = await ctx.bot.user_manager.get_config(ctx.author.id)

        if not (todo := user_config.get_todo(todo_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"You don't have a todo with id **{todo_id}**."
            )

        return todo


class TodoContentConverter(commands.clean_content):

    async def convert(self, ctx: custom.Context, argument: str) -> str:

        if not (argument := (await super().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if len(argument) > 150:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Your todo content must be under 150 characters."
            )

        return argument
