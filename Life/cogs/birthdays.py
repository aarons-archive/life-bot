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
from utilities import context, converters, exceptions, utils


class Birthdays(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.default_birthday = pendulum.DateTime(2020, 1, 1, tzinfo=pendulum.timezone('UTC'))

    @commands.group(name='birthdays', aliases=['birthday', 'bd'], invoke_without_command=True)
    async def birthdays(self, ctx: context.Context, *, person: discord.Member = None) -> None:
        """
        Display the birthday of you, or the member provided.

        `person`: The person to display the birthday of. Can be their name, id or mention. If this argument is not passed the command will display your birthday.
        """

        if person is None:
            person = ctx.author

        user_config = self.bot.user_manager.get_config(user_id=person.id)

        if user_config.birthday == self.default_birthday:
            raise exceptions.ArgumentError(f'`{person}` has not set their birthday.')
        if user_config.birthday_private and ctx.author.id != person.id:
            raise exceptions.ArgumentError(f'`{person}` has their birthday set as private.')

        embed = discord.Embed(
                colour=user_config.colour,
                title=f'`{person.name}`\'s birthday information:',
                description=f'`Birthday:` {utils.format_date(datetime=user_config.birthday)}\n'
                            f'`Next birthday:` In {utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
                            f'`Age:` {user_config.age}\n',
        )
        await ctx.send(embed=embed)

    @birthdays.command(name='set')
    async def birthdays_set(self, ctx: context.Context, *, date: converters.DatetimeConverter) -> None:
        """
        Set your birthday.

        `date`: Your birthday. This should include some form of date such as `tomorrow`, `in 3 weeks` or `1st january 2020`. Your birthday must allow you to be at least 13 years old and not more than 150.
        """

        entries = {index: (date_phrase, datetime) for index, (date_phrase, datetime) in enumerate(date['found'].items())}
        if len(entries) != 1:
            choice = await ctx.paginate_choice(
                    entries=[f'`{index + 1}.` **{phrase}**\n`{utils.format_date(datetime=datetime)}`' for index, (phrase, datetime) in entries.items()],
                    per_page=10, header=f'**Multiple dates were detected within your query, please select the one that best matches your birthday:**\n\n'
            )
            result = entries[choice]
        else:
            result = entries[0]

        if result[1] > pendulum.now(tz='UTC').subtract(years=13) or result[1] < pendulum.now(tz='UTC').subtract(years=150):
            raise exceptions.ArgumentError('You must be more than 13 (As per discord TOS) and less than 150 years old.')

        await self.bot.user_manager.set_birthday(user_id=ctx.author.id, birthday=result[1])
        await ctx.send(f'Your birthday has been set to `{utils.format_date(datetime=ctx.user_config.birthday)}`.')

    @birthdays.command(name='reset')
    async def birthdays_reset(self, ctx: context.Context) -> None:
        """
        Reset your birthday.
        """

        await self.bot.user_manager.set_birthday(user_id=ctx.author.id, birthday=pendulum.date(2020, 1, 1))
        await ctx.send('Your birthday was reset.')

    @birthdays.command(name='private')
    async def birthdays_private(self, ctx: context.Context) -> None:
        """
        Make your birthday private.
        """

        if ctx.user_config.birthday_private is True:
            raise exceptions.GeneralError('Your birthday is already private.')

        await self.bot.user_manager.set_birthday(user_id=ctx.author.id, private=True)
        await ctx.send('Your birthday is now private.')

    @birthdays.command(name='public')
    async def birthdays_public(self, ctx: context.Context) -> None:
        """
        Make your birthday public.
        """

        if ctx.user_config.birthday_private is False:
            raise exceptions.GeneralError('Your birthday is already public.')

        await self.bot.user_manager.set_birthday(user_id=ctx.author.id, private=False)
        await ctx.send('Your birthday is now public.')

    @birthdays.command(name='upcoming')
    async def birthdays_upcoming(self, ctx: context.Context) -> None:
        """
        Display a list of upcoming birthdays within the server.
        """

        configs = dict(
                sorted(
                        filter(
                                lambda c: ctx.guild.get_member(c[1].id) is not None and (c[1].birthday_private is False and c[1].birthday != self.default_birthday),
                                self.bot.user_manager.configs.items()
                        ),
                        key=lambda config: config[1].next_birthday
                )
        )
        if not configs:
            raise exceptions.ArgumentError('There are no users who have set their birthday in this server, or everyone has them private.')

        embed = discord.Embed(colour=ctx.colour, title=f'Upcoming birthdays (First 3): ')
        for user_id, user_config in list(configs.items())[:3]:
            embed.add_field(
                    name=f'{ctx.guild.get_member(user_id)}',
                    value=f'`Birthday:` {utils.format_date(datetime=user_config.birthday)}\n'
                          f'`Next birthday:` In {utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
                          f'`Current age:` {user_config.age}',
                    inline=False
            )

        await ctx.send(embed=embed)

    @birthdays.command(name='list')
    async def birthdays_list(self, ctx: context.Context) -> None:
        """
        Display a list of birthdays within the server.
        """

        configs = dict(
                sorted(
                        filter(
                                lambda c: ctx.guild.get_member(c[1].id) is not None and (c[1].birthday_private is False and c[1].birthday != self.default_birthday),
                                self.bot.user_manager.configs.items()
                        ),
                        key=lambda config: config[1].next_birthday
                )
        )
        if not configs:
            raise exceptions.ArgumentError('There are no users who have set their birthday in this server, or everyone has them private.')

        entries = [
            f'**{ctx.guild.get_member(user_id)}**\n'
            f'`Birthday:` {utils.format_date(datetime=user_config.birthday)}\n'
            f'`Next birthday:` In {utils.format_difference(datetime=user_config.next_birthday.subtract(days=1), suppress=[])}\n'
            f'`Current age:` {user_config.age}\n'
            for user_id, user_config in configs.items()
        ]
        await ctx.paginate_embed(entries=entries, per_page=3, title='Upcoming birthdays: ')

    @birthdays.command(name='next')
    async def birthdays_next(self, ctx: context.Context) -> None:
        """
        Display the next person to have a birthday within the server.
        """

        configs = dict(
                sorted(
                        filter(
                                lambda c: ctx.guild.get_member(c[1].id) is not None and (c[1].birthday_private is False and c[1].birthday != self.default_birthday),
                                self.bot.user_manager.configs.items()
                        ),
                        key=lambda config: config[1].next_birthday
                )
        )

        if not configs:
            raise exceptions.ArgumentError('There are no users who have set their birthday in this server, or everyone has them private.')

        first = list(configs.items())[0]
        member = ctx.guild.get_member(first[0])

        embed = discord.Embed(colour=ctx.colour, title=f'The next person to have a birthday is:')
        embed.add_field(name=f'**{member}**',
                        value=f'`Birthday:` {utils.format_date(datetime=first[1].birthday)}\n'
                              f'`Next birthday:` In {utils.format_difference(datetime=first[1].next_birthday.subtract(days=1), suppress=[])}\n'
                              f'`Age:` {first[1].age}\n')
        await ctx.send(embed=embed)


def setup(bot: Life):
    bot.add_cog(Birthdays(bot=bot))
