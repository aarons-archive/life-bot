import discord
import pendulum
from discord.ext import commands

from core import colours, emojis
from core.bot import Life
from utilities import context, converters, enums, exceptions, objects, utils


def setup(bot: Life) -> None:
    bot.add_cog(Reminders(bot=bot))


class Reminders(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name="remind", aliases=["remindme"])
    async def remind(self, ctx: context.Context, *, when: converters.DatetimeConverter) -> None:
        """
        Creates a reminder.

        **when**: The subject you want to be reminded about, should include some form of time such as **tomorrow**, **10am**, or **3 hours**.

        **Usage:**
        `l-remind in 3 hours do that thing you talked about doing.`
        """

        entries = {index: (phrase, datetime) for index, (phrase, datetime) in enumerate(when[1].items())}

        choice = await ctx.choice(
                entries=[f"**{index + 1}:** **{phrase}**\n`{utils.format_datetime(datetime)}`" for index, (phrase, datetime) in entries.items()],
                per_page=5,
                splitter="\n\n",
                title="Multiple dates/times where detected in your reminder:",
                header="Choose the option that best matches your intended reminder time.\n\n"
        )
        _, datetime = entries[choice]

        if datetime < pendulum.now(tz='UTC'):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="The date/time detected was in the past.")

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        reminder = await user_config.create_reminder(
                channel_id=ctx.channel.id,
                datetime=datetime,
                content=await utils.safe_content(self.bot.mystbin, when[0], max_characters=1500),
                jump_url=ctx.message.jump_url
        )

        embed = discord.Embed(
                colour=colours.GREEN,
                description=f"Reminder with id **{reminder.id}** created for **{utils.format_datetime(reminder.datetime)}**, which is in **{utils.format_difference(reminder.datetime)}**."
        )
        await ctx.reply(embed=embed)

    @commands.group(name="reminders", aliases=["reminder"], invoke_without_command=True)
    async def _reminders(self, ctx: context.Context) -> None:
        """
        Base reminder command, displays a list of active reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not (reminders := [reminder for reminder in user_config.reminders.values() if not reminder.done]):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You do not have any active reminders.")

        entries = [
            f"**{reminder.id}:** [__**In {utils.format_difference(reminder.datetime)}**__]({reminder.jump_url})\n"
            f"**When:** {utils.format_datetime(reminder.datetime, seconds=True)}\n"
            f"**Repeat:** {reminder.repeat_type.name.replace('_', ' ').lower().title()}\n"
            f"**Content:** {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}\n"
            for reminder in sorted(reminders, key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(
                entries=entries,
                per_page=5,
                title=f"Active reminders for **{ctx.author}**:"
        )

    @_reminders.command(name="list", aliases=["l"])
    async def _reminders_list(self, ctx: context.Context) -> None:
        """
        Alias of the base reminder command.
        """

        await ctx.invoke(self._reminders)

    @_reminders.command(name="all", aliases=["a"])
    async def _reminders_all(self, ctx: context.Context) -> None:
        """
        Displays a list of all your reminders.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.reminders:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You do not have any reminders.")

        entries = [
            f"**{reminder.id}:** [__**{'In ' if not reminder.done else ''}{utils.format_difference(reminder.datetime)}{' ago' if reminder.done else ''}**__]({reminder.jump_url})\n"
            f"**When:** {utils.format_datetime(reminder.datetime, seconds=True)}\n"
            f"**Repeat:** {reminder.repeat_type.name.replace('_', ' ').lower().title()}\n"
            f"**Content:** {await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=80)}\n"
            for reminder in sorted(user_config.reminders.values(), key=lambda reminder: reminder.datetime)
        ]

        await ctx.paginate_embed(
                entries=entries,
                per_page=5,
                title=f"Reminders for **{ctx.author}**:"
        )

    @_reminders.command(name="edit")
    async def _reminders_edit(self, ctx: context.Context, reminder: objects.Reminder, *, content: str) -> None:
        """
        Edits a reminders content.

        `reminder`: The id of the reminder to edit.
        `content`: The content to edit the reminder with.
        """

        content = await utils.safe_content(self.bot.mystbin, content, max_characters=1500)
        await reminder.change_content(content, jump_url=ctx.message.jump_url)

        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Edited content of reminder with id **{reminder.id}**."))

        #

    @_reminders.command(name="delete")
    async def _reminders_delete(self, ctx: context.Context, reminders: commands.Greedy[objects.Reminder]) -> None:
        """
        Deletes reminders with the given id's.

        **reminders**: A list of reminders id's to delete, separated by spaces.
        """

        if not reminders:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"One or more of the reminder id's provided were invalid.")

        for reminder in reminders:
            await reminder.delete()

        s = "s" if len(reminders) > 1 else ""

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Deleted **{len(reminders)}** reminder{s} with id{s} {', '.join(f'**{reminder.id}**' for reminder in reminders)}.")
        await ctx.reply(embed=embed)

    @_reminders.command(name="repeat")
    async def _reminders_repeat(self, ctx: context.Context, reminder: objects.Reminder, *, repeat_type: enums.ReminderRepeatType) -> None:
        """
        Edits a reminders repeat type.

        **reminder**: The id of the reminder to edit.
        **repeat_type**: The repeat type to set for the reminder.
        """

        if reminder.done:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"That reminder is already done.")

        await reminder.change_repeat_type(repeat_type)
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Edited repeat type of reminder with id **{reminder.id}**."))

    @_reminders.command(name="info")
    async def _reminders_info(self, ctx: context.Context, reminder: objects.Reminder) -> None:
        """
        Displays information about a reminder.
        """

        embed = discord.Embed(
                colour=colours.MAIN,
                title=f"Information for reminder **{reminder.id}:**",
                description=f"[__**{'In ' if not reminder.done else ''}{utils.format_difference(reminder.datetime)}{' ago' if reminder.done else ''}:**__]({reminder.jump_url})\n"
                            f"**Created:** {utils.format_datetime(reminder.created_at, seconds=True)}\n"
                            f"**When:** {utils.format_datetime(reminder.datetime, seconds=True)}\n"
                            f"**Repeat:** {reminder.repeat_type.name.replace('_', ' ').lower().title()}\n"
                            f"**Done:** {str(reminder.done).replace('False', 'No').replace('True', 'Yes')}\n"
                            f"**Content:**\n\n"
                            f"{await utils.safe_content(self.bot.mystbin, reminder.content, max_characters=1000)}"
        )
        await ctx.reply(embed=embed)
