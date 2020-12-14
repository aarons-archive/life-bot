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
    async def birthday(self, ctx: context.Context, *, person: converters.UserConverter = None) -> None:
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
            raise exceptions.ArgumentError(f'`{person}` has their birthday set to be private.')

        embed = discord.Embed(description=f'`{person.name}`**\'s birthday information:**\n\n'
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

        entries = {index: (date_phrase, datetime) for index, (date_phrase, datetime) in enumerate(date['found'].items())}

        if len(entries) != 1:
            result = await ctx.paginate_choice(
                    entries=[f'`{index + 1}.` **{datetime_phrase}**\n`{self.bot.utils.format_date(datetime=datetime)}`' for index, (datetime_phrase, datetime) in entries.items()],
                    per_page=10, header=f'**Multiple dates were detected within your query, please select the one that best matches your birthday:**\n\n'
            )
        else:
            result = entries[0]

        datetime = result[1]

        now = pendulum.now()
        if datetime > now.subtract(years=13) or datetime < now.subtract(years=150):
            raise exceptions.ArgumentError('You must be more than 13 (As per discord TOS) and less than 150 years old.')

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday, operation=Operations.set, value=datetime)
        await ctx.send(f'Your birthday has been set to `{self.bot.utils.format_date(datetime=ctx.user_config.birthday)}`.')

    @birthday.command(name='reset')
    async def birthday_reset(self, ctx: context.Context) -> None:
        """
        Resets your birthday.
        """

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, editable=Editables.birthday, operation=Operations.reset)
        await ctx.send('Your birthday was reset.')

    @birthday.command(name='private')
    async def birthday_private(self, ctx: context.Context) -> None:
        """
        Toggles your birthday being publicly available or not.
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

        configs = sorted(self.bot.user_manager.configs.items(), key=lambda user_config: user_config[1].birthday)
        birthdays = {}

        for user_id, config in configs:

            member = ctx.guild.get_member(user_id)
            if not member:
                continue

            if config.birthday_private or config.birthday == pendulum.DateTime(2020, 1, 1, 0, 0, 0, tzinfo=pendulum.timezone('UTC')):
                continue

            birthdays[member] = config

        if not birthdays:
            raise exceptions.ArgumentError('There are no users who have set their birthday in this server, or everyone has them private.')

        birthdays_format = "\n\n".join(
            f'__**`{person.name}`\'s birthday:**__\n'
            f'`Birthday:` {self.bot.utils.format_date(datetime=user_config.birthday)}\n'
            f'`Next birthday:` In {self.bot.utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
            f'`Current age:` {user_config.age}'
            for person, user_config in list(birthdays.items())[:5]
        )

        embed = discord.Embed(description=f'**Upcoming birthdays:**\n\n{birthdays_format}', colour=ctx.colour)
        await ctx.send(embed=embed)

    @birthday.command(name='next')
    async def birthday_next(self, ctx: context.Context) -> None:
        """
        Displays the next person to have a birthday within the server.
        """

        configs = sorted(self.bot.user_manager.configs.items(), key=lambda user_config: user_config[1].birthday)
        birthdays = {}

        for user_id, config in configs:

            member = ctx.guild.get_member(user_id)
            if not member:
                continue

            if config.birthday_private or config.birthday == pendulum.DateTime(2020, 1, 1, 0, 0, 0, tzinfo=pendulum.timezone('UTC')):
                continue

            birthdays[member] = config

        if not birthdays:
            raise exceptions.ArgumentError('There are no users who have set their birthday in this server, or everyone has them private.')

        birthday = list(birthdays.items())[0]

        embed = discord.Embed(description=f'**The next person to have a birthday is:**\n\n'
                                          f'__**`{birthday[0].name}`:**__\n'
                                          f'`Birthday:` {self.bot.utils.format_date(datetime=birthday[1].birthday)}\n'
                                          f'`Next birthday:` In {self.bot.utils.format_difference(datetime=birthday[1].next_birthday.subtract(days=1), suppress=[])}\n'
                                          f'`Age:` {birthday[1].age}\n', colour=ctx.colour)
        await ctx.send(embed=embed)


def setup(bot: Life):
    bot.add_cog(Birthdays(bot=bot))
