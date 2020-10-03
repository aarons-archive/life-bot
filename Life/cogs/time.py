"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio

import discord
import pendulum
import wolframalpha
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.bot.wolframalpha = wolframalpha.Client(self.bot.config.wolframalpha_token)

    @commands.command(name='timezones', aliases=['tzs'])
    async def timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(entries=pendulum.timezones, per_page=20, title='Available timezones:', url=f'{self.bot.dashboard}timezones')

    @commands.group(name='time', invoke_without_command=True)
    async def time(self, ctx: context.Context, *, timezone: str = None) -> None:
        """
        Displays the time of the member or the timezone provided.

        `timezone`: The timezone or members name, id or mention that you want to get.
        """

        if not timezone:
            member = ctx.author
            timezone = ctx.user_config.timezone
        else:
            try:
                member = None
                timezone = await converters.TimezoneConverter().convert(ctx=ctx, argument=timezone)
            except exceptions.ArgumentError as error:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=timezone)
                    timezone = self.bot.user_manager.get_user_config(user_id=member.id).timezone
                except commands.BadArgument:
                    raise exceptions.ArgumentError(str(error))

        datetime = self.bot.utils.format_datetime(datetime=pendulum.now(tz=timezone))

        embed = discord.Embed(colour=ctx.user_config.colour, title=f'Time in {timezone.zone} {f"({member})" if member else ""}', description=f'```py\n{datetime}\n```')
        await ctx.send(embed=embed)

    @time.command(name='set')
    async def time_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone to the one specified.

        See https://dashboard.mrrandom.xyz/timezones for a full list of available timezones.

        `timezone`: The timezone to use.
        """

        await self.bot.user_manager.set_user_config(user_id=ctx.author.id, attribute='timezone', value=timezone.name)
        await ctx.send(f'Your timezone has been set to `{timezone.name}`.')

    @time.command(name='clear')
    async def time_clear(self, ctx: context.Context) -> None:
        """
        Resets your timezone back to the default (UTC).
        """

        await self.bot.user_manager.set_user_config(user_id=ctx.author.id, attribute='timezone', value='UTC')
        await ctx.send(f'Your timezone has been reset back to the default of `UTC`.')

    @commands.group(name='remind', aliases=['reminders'])
    async def remind(self, ctx: context.Context, *, reminder: converters.DatetimeParser) -> None:

        async with ctx.typing():

            entries = [datetime for datetime in reminder['results'].values()]

            paginator = await ctx.paginate_embed(entries=[f'`{index + 1}.` `{self.bot.utils.format_datetime(datetime=entry)}`' for index, entry in enumerate(entries)],
                                                 per_page=10, header=f'__**Select the datetime you would like to be reminded at:**__\n\n'
                                                                     f'**Interpreted time:**\n{reminder["input_interpretation"]}\n\n')

            try:
                response = await self.bot.wait_for('message', check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30.0)
            except asyncio.TimeoutError:
                raise exceptions.ArgumentError('You took too long to respond.')

            response = await self.bot.clean_content_converter.convert(ctx=ctx, argument=response.content)
            try:
                response = int(response) - 1
            except ValueError:
                raise exceptions.ArgumentError('That was not a valid number.')
            if response < 0 or response >= len(entries):
                raise exceptions.ArgumentError('That was not one of the available datetimes.')

            await paginator.stop()
            result = entries[response]

            embed = discord.Embed(colour=ctx.colour, title='Reminder created:')
            embed.description = f'**When:**\n`{self.bot.utils.format_datetime(datetime=result)}`\n' \
                                f'**Content:**\n{reminder["input"]}\n\n' \
                                f'You can use the `{ctx.prefix}{self.bot.get_command("time set").qualified_name}` command to set a timezone what will be used when ' \
                                f'choosing a reminder datetime.'

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Time(bot))
