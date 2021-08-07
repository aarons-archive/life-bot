from discord.ext import commands

from core import colours, emojis, values
from utilities import context, enums, exceptions, objects


class ReminderConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> objects.Reminder:

        try:
            reminder_id = int(argument)
        except ValueError:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="That was not a valid reminder id.")

        user_config = await ctx.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminder := user_config.get_reminder(reminder_id)):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You do not have a reminder with that id.")

        return reminder


class ReminderRepeatTypeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> enums.ReminderRepeatType:

        if enum := getattr(enums.ReminderRepeatType, argument.replace(" ", "_").upper(), None):
            return enum

        valid = [f"{repeat_type.name.replace('_', ' ').lower()}" for repeat_type in enums.ReminderRepeatType]
        raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"Repeat type must be one of:\n{f'{values.NL}'.join([f'- {v}' for v in valid])}")
