# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import custom, exceptions, objects


class ReminderConverter(commands.Converter):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.Reminder:

        try:
            reminder_id = int(argument)
        except ValueError:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="That was not a valid reminder id."
            )

        user_config = await ctx.bot.user_manager.get_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="You do not have a reminder with that id."
            )

        return reminder
