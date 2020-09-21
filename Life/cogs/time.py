import datetime as dt

import discord
import pytz
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='timezones', aliases=['tzs'])
    async def timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(entries=pytz.all_timezones, per_page=20, title='Available timezones:', url=f'{self.bot.dashboard}timezones')

    @commands.group(name='time', invoke_without_command=True)
    async def time(self, ctx: context.Context, *, timezone: str = None) -> None:
        """
        Displays the time of the member or the timezone provided.

        `timezone`: The timezone or members name, id or mention that you want to get.
        """

        if not timezone:
            member = ctx.author
            timezone = ctx.user_config.pytz

        else:
            try:
                member = None
                timezone = await self.bot.timezone_converter.convert(ctx=ctx, argument=timezone)
            except exceptions.ArgumentError as error:
                try:
                    member = await self.bot.member_converter.convert(ctx=ctx, argument=timezone)
                    timezone = self.bot.get_user_config(user=member).pytz
                except commands.BadArgument:
                    raise exceptions.ArgumentError(str(error))

        datetime = self.bot.utils.format_datetime(datetime=dt.datetime.now(tz=timezone))

        embed = discord.Embed(colour=ctx.user_config.colour, title=f'Time in {timezone.zone} {f"({member})" if member else ""}', description=f'```py\n{datetime}\n```')
        await ctx.send(embed=embed)

    @time.command(name='set')
    async def time_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter):
        """
        Sets your timezone to the one specified.

        See https://dashboard.mrrandom.xyz/timezones/ for a full list of available timezones.

        `timezone`: The timezone to use.
        """

        await self.bot.set_user_config(user=ctx.author, attribute='timezone', value=timezone.zone)
        await ctx.send(f'Set your timezone to `{timezone.zone}`.')

    @time.command(name='clear')
    async def time_clear(self, ctx: context.Context):
        """
        Sets your timezone back to default (UTC).
        """

        await self.bot.set_user_config(user=ctx.author, attribute='timezone', value='UTC')
        await ctx.send(f'Reset your timezone.')


def setup(bot):
    bot.add_cog(Time(bot))

