#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

import asyncio

import discord
import pendulum
from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions
from utilities.enums import Editables, Operations


class Birthdays(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name='birthday', aliases=['birthdays', 'bd'], invoke_without_command=True)
    async def birthday(self, ctx: context.Context, person: converters.UserConverter = None) -> None:
        """
        Displays the birthday of you, or the member provided.

        `person`: The person to display the birthday of. Can be their name, id or mention. If this argument is not passed the command will display your birthday.
        """

        if person is None:
            person = ctx.author

        user_config = self.bot.user_manager.get_user_config(user_id=person.id)

        if user_config.birthday == pendulum.DateTime(2020, 1, 1, 0, 0, 0, tzinfo=pendulum.timezone('UTC')):
            raise exceptions.ArgumentError(f'`{person}` has not set their birthday.')
        if user_config.birthday_private and ctx.author.id != person.id:
            raise exceptions.ArgumentError(f'`{person}\'s` birthday is private.')

        embed = discord.Embed(description=f'**{person}\'s birthday information:**\n\n'
                                          f'`Birthday:` {self.bot.utils.format_date(datetime=user_config.birthday)}\n'
                                          f'`Next birthday:` In {self.bot.utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
                                          f'`Age:` {user_config.age}\n',
                              colour=user_config.colour)

        await ctx.send(embed=embed)

    @birthday.command(name='set')
    async def birthday_set(self, ctx: context.Context, *, date: converters.DatetimeConverter) -> None:
        """
        Sets your birthday.

        `date`: Your birthday. This should include some form of date such as `tomorrow`, `in 3 weeks` or `1st january 2020`. Your birthday must allow you to be at least 13 years old and not more than 150.
        """

        entries = {index: (datetime_phrase, datetime) for index, (datetime_phrase, datetime) in enumerate(date['found'].items())}

        if len(entries) == 1:
            result = entries[0]

        else:

            paginator = await ctx.paginate_embed(entries=[
                f'`{index + 1}.` **{datetime_phrase}**\n`{self.bot.utils.format_date(datetime=datetime)}`' for index, (datetime_phrase, datetime) in entries.items()],
                per_page=10, header=f'**Multiple time and/or dates were detected within your query, please select the one that matches your birthday:**\n\n'
            )

            try:
                response = await self.bot.wait_for('message', check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout=30.0)
            except asyncio.TimeoutError:
                raise exceptions.ArgumentError('You took too long to respond.')

            response = await commands.clean_content().convert(ctx=ctx, argument=response.content)
            try:
                response = int(response) - 1
            except ValueError:
                raise exceptions.ArgumentError('That was not a valid number.')
            if response < 0 or response >= len(entries):
                raise exceptions.ArgumentError('That was not one of the available options.')

            await paginator.stop()
            result = entries[response]

        datetime = result[1]

        if not datetime.day or not datetime.month or not datetime.year:
            raise exceptions.ArgumentError('That datetime did not have a year, month or day.')

        now = pendulum.now()
        if datetime > now.subtract(years=13) or datetime < now.subtract(years=150):
            raise exceptions.ArgumentError('You must be older than `13` and cant be more than `150` years old.')

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday, operation=Operations.set, value=datetime)
        await ctx.send(f'Your birthday has been set to `{self.bot.utils.format_date(datetime=ctx.user_config.birthday)}`.')

    @commands.command(name='reset')
    async def birthday_reset(self, ctx: context.Context) -> None:
        """
        Resets your birthday.
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday, operation=Operations.reset)
        await ctx.send('Your birthday was reset.')

    @birthday.command(name='private')
    async def birthday_private(self, ctx: context.Context) -> None:
        """
        Toggles your birthday being private or public.
        """

        if ctx.user_config.birthday_private is False:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday_private, operation=Operations.set)
            await ctx.send('Your birthday is now private.')
        else:
            await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday_private, operation=Operations.reset)
            await ctx.send('Your birthday is now public.')

    @birthday.command(name='upcoming')
    async def birthday_upcoming(self, ctx: context.Context) -> None:
        """
        Displays a list of upcoming birthdays within the server.
        """

        configs = sorted(self.bot.user_manager.configs.items(), key=lambda kv: kv[1].birthday)
        birthdays = {}

        for user_id, config in configs:

            member = ctx.guild.get_member(user_id)
            if not member:
                continue

            if config.birthday_private or config.birthday == pendulum.DateTime(2020, 1, 1, 0, 0, 0, tzinfo=pendulum.timezone('UTC')):
                continue

            birthdays[member] = config

        if not birthdays:
            raise exceptions.ArgumentError('There are no users with birthdays set in this server.')

        birthdays_format = "\n\n".join(
            f'__**{person}:**__\n'
            f'`Birthday:` {self.bot.utils.format_date(datetime=user_config.birthday)}\n'
            f'`Next birthday:` In {self.bot.utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
            f'`Current age:` {user_config.age}'
            for person, user_config in list(birthdays.items())[:10]
        )

        embed = discord.Embed(description=f'**Upcoming birthdays:**\n\n{birthdays_format}', colour=ctx.colour)
        await ctx.send(embed=embed)

    @birthday.command(name='next')
    async def birthday_next(self, ctx: context.Context) -> None:
        """
        Displays the birthday of the next person to have one within the server.
        """

        configs = sorted(self.bot.user_manager.configs.items(), key=lambda kv: kv[1].birthday)
        birthdays = {}

        for user_id, config in configs:

            member = ctx.guild.get_member(user_id)
            if not member:
                continue

            if config.birthday_private or config.birthday == pendulum.DateTime(2020, 1, 1, 0, 0, 0, tzinfo=pendulum.timezone('UTC')):
                continue

            birthdays[member] = config

        if not birthdays:
            raise exceptions.ArgumentError('There are no users with birthdays set in this server.')

        birthdays = list(birthdays.items())[0]

        embed = discord.Embed(description=f'**The next person to have a birthday is:**\n\n'
                                          f'**{birthdays[0]}:**\n'
                                          f'`Birthday:` {self.bot.utils.format_date(datetime=birthdays[1].birthday)}\n'
                                          f'`Next birthday:` In {self.bot.utils.format_difference(datetime=birthdays[1].next_birthday.subtract(days=1), suppress=[])}\n'
                                          f'`Current age:` {birthdays[1].age}', colour=ctx.colour)
        await ctx.send(embed=embed)


def setup(bot: Life):
    bot.add_cog(Birthdays(bot=bot))
