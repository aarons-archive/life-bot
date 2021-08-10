import collections
from typing import Optional

import discord
import pendulum
import rapidfuzz
from discord.ext import commands
from pendulum.tz.timezone import Timezone
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone

from core import colours, emojis, values
from core.bot import Life
from utilities import context, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Time(bot=bot))


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="times")
    async def times(self, ctx: context.Context) -> None:
        """
        Displays a list of people and their timezones.
        """

        if not (timezones := self.bot.user_manager.timezones(guild_id=ctx.guild.id)):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="No one has set their timezone, or everyone has set them to be private.")

        timezone_users = collections.defaultdict(list)

        for user_config in timezones:
            timezone_users[user_config.time.format("HH:mm (ZZ)")].append(f"{ctx.guild.get_member(user_config.id)} - {user_config.timezone.name}")

        await ctx.paginate_embed(
                entries=[f"`{timezone}:`\n{values.NL.join(members)}\n" for timezone, members in timezone_users.items()],
                per_page=5,
                title=f"Timezones for **{ctx.guild}:**"
        )

    @commands.command(name="timezones", aliases=["tzs"])
    async def timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(
                entries=list(pendulum.timezones),
                per_page=20,
                title="Available timezones:", header="Click [here](https://skeletonclique.axelancerr.xyz/timezones) to view a list of timezones.\n\n"
        )

    #

    @commands.group(name="timezone", aliases=["time"], invoke_without_command=True)
    async def _timezone(self, ctx: context.Context, *, timezone: Optional[str]) -> None:
        """
        Displays the time of the user or timezone provided.

        **timezone**: The timezone or users Name, Nickname, ID, or @Mention that you want to get.
        """

        author_user_config = await self.bot.user_manager.get_config(ctx.author.id)
        member: Optional[discord.Member] = None

        if not timezone:
            member = ctx.author
            found_timezone = author_user_config.timezone
        else:
            try:
                found_timezone = pendulum.timezone(timezone)
            except InvalidTimezone:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=timezone)
                except commands.BadArgument:
                    msg = "\n".join(f"- {match}" for match, _, _ in rapidfuzz.process.extract(query=timezone, choices=pendulum.timezones))
                    raise exceptions.EmbedError(colour=colours.RED, description=f"I did not recognise that timezone or user. Maybe you meant one of these?\n{msg}")
                else:
                    if (user_config := await self.bot.user_manager.get_config(member.id)).timezone_private is True and member.id != ctx.author.id:
                        raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="That users timezone is private.")
                    found_timezone = user_config.timezone

        if not found_timezone:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="That user has not set their timezone.")

        embed = discord.Embed(
                colour=colours.MAIN,
                title=f"Time in **{found_timezone.name}**{f' for **{member}**' if member else ''}:",
                description=f"```\n{utils.format_datetime(pendulum.now(tz=found_timezone))}\n```"
        )
        await ctx.reply(embed=embed)

    @commands.guild_only()
    @_timezone.command(name="card")
    async def _timezone_card(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all servers members.
        """

        async with ctx.typing():
            file = await self.bot.user_manager.create_timecard(guild_id=ctx.guild.id)
            await ctx.reply(file=file)

    @_timezone.command(name="set")
    async def _timezone_set(self, ctx: context.Context, *, timezone: Timezone) -> None:
        """
        Sets your timezone.

        **timezone**: The timezone to use. See [here](https://skeletonclique.axelancerr.xyz/timezones) for a list of timezones in an easier to navigate format.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        await user_config.set_timezone(timezone)

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Your timezone has been set to **{user_config.timezone.name}**.")
        await ctx.reply(embed=embed)

    @_timezone.command(name="reset")
    async def _timezone_reset(self, ctx: context.Context) -> None:
        """
        Resets your timezone.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        await user_config.set_timezone()

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Your timezone has been reset back to `{user_config.timezone.name}`.")
        await ctx.reply(embed=embed)

    @_timezone.command(name="private")
    async def _timezone_private(self, ctx: context.Context) -> None:
        """
        Make your timezone private.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if user_config.timezone_private is True:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Your timezone is already **private**.")

        await user_config.set_timezone(user_config.timezone, private=True)

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description="Your timezone is now **private**.")
        await ctx.reply(embed=embed)

    @_timezone.command(name="public")
    async def _timezone_public(self, ctx: context.Context) -> None:
        """
        Make your timezone public.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if user_config.timezone_private is False:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Your timezone is already **public**.")

        await user_config.set_timezone(user_config.timezone, private=True)

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description="Your timezone is now **public**.")
        await ctx.reply(embed=embed)
