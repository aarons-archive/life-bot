from typing import Optional

import discord
import pendulum
import rapidfuzz
from discord.ext import commands
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone

from core import colours, values
from core.bot import Life
from utilities import context, converters, exceptions, utils


class Time(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='times')
    async def times(self, ctx: context.Context) -> None:
        """
        Displays a list of people and what timezone they are in.
        """

        if not (timezones := self.bot.user_manager.timezones(guild_id=getattr(ctx.guild, 'id', None))):
            raise exceptions.ArgumentError('There are no users who have set their timezone, or everyone has set them to be private.')

        timezone_users = {}

        for user_config in timezones:

            user = ctx.guild.get_member(user_config.id) if ctx.guild else self.bot.get_user(user_config.id)
            timezone = user_config.time.format('HH:mm (ZZ)')

            if users := timezone_users.get(timezone, []):
                if len(users) > 36:
                    break
                timezone_users[timezone].append(f'{user} - {user_config.timezone.name}')
            else:
                timezone_users[timezone] = [f'{user} - {user_config.timezone.name}']

        entries = [f'`{timezone}:`\n{values.NL.join(members)}\n' for timezone, members in timezone_users.items()]
        await ctx.paginate_embed(entries=entries, per_page=5, title=f'{ctx.guild}\'s timezones:')

    @commands.command(name='timezones', aliases=['tzs'])
    async def _timezones(self, ctx: context.Context) -> None:
        """
        Displays a list of timezones that can be used with the bot.
        """

        await ctx.paginate_embed(
                entries=list(pendulum.timezones), per_page=20,
                title='Available timezones:', header='Click [here](https://skeletonclique.mrrandom.xyz/timezones) to view a list of timezones.\n\n'
        )

    #

    @commands.group(name='timezone', aliases=['time'], invoke_without_command=True)
    async def _timezone(self, ctx: context.Context, *, timezone: Optional[str]) -> None:
        """
        Displays the time of the member or timezone provided.

        `timezone`: The timezone or members Name, Nickname, ID, or @Mention that you want to get.
        """

        member: Optional[discord.Member] = None

        if not timezone:
            member = ctx.author
            found_timezone = ctx.user_config.timezone
        else:
            try:
                found_timezone = pendulum.timezone(timezone)
            except InvalidTimezone:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=timezone)
                except commands.BadArgument:
                    msg = '\n'.join(f'- `{match}`' for match, _, _ in rapidfuzz.process.extract(query=timezone, choices=pendulum.timezones, processor=lambda s: s))
                    raise exceptions.ArgumentError(f'I did not recognise that timezone or member. Maybe you meant one of these?\n{msg}')
                else:
                    if (user_config := self.bot.user_manager.get_config(member.id)).timezone_private is True and member.id != ctx.author.id:
                        raise exceptions.ArgumentError('That users timezone is private.')
                    found_timezone = user_config.timezone

        if not found_timezone:
            raise exceptions.ArgumentError('That user has not set their timezone.')

        embed = discord.Embed(
                colour=colours.MAIN,
                title=f'Time in `{found_timezone.name}`{f" for `{member}`" if member else ""}:',
                description=f'```\n{utils.format_datetime(pendulum.now(tz=found_timezone))}\n```'
        )
        await ctx.reply(embed=embed)

    @_timezone.command(name='card')
    async def timecard(self, ctx: context.Context) -> None:
        """
        Creates an image with the timezones of all servers members.
        """

        async with ctx.typing():
            file = await self.bot.user_manager.create_timecard(guild_id=getattr(ctx.guild, 'id', None))
            await ctx.reply(file=file)

    @_timezone.command(name='set')
    async def _timezone_set(self, ctx: context.Context, *, timezone: converters.TimezoneConverter) -> None:
        """
        Sets your timezone.

        `timezone`: The timezone to use. See [here](https://skeletonclique.mrrandom.xyz/timezones) for a list of timezones in an easier to navigate format.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        # noinspection PyTypeChecker
        await user_config.set_timezone(timezone)
        await ctx.reply(f'Your timezone has been set to `{user_config.timezone.name}`.')

    @_timezone.command(name='reset')
    async def _timezone_reset(self, ctx: context.Context) -> None:
        """
        Resets your timezone information.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        await user_config.set_timezone(pendulum.timezone('UTC'))
        await ctx.reply(f'Your timezone has been reset back to `{user_config.timezone.name}`.')

    @_timezone.command(name='private')
    async def _timezone_private(self, ctx: context.Context) -> None:
        """
        Make your timezone private.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if user_config.timezone_private is True:
            raise exceptions.ArgumentError('Your timezone is already private.')

        await user_config.set_timezone(user_config.timezone, private=True)
        await ctx.reply('Your timezone is now private.')

    @_timezone.command(name='public')
    async def _timezone_public(self, ctx: context.Context) -> None:
        """
        Make your timezone public.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if user_config.timezone_private is False:
            raise exceptions.ArgumentError('Your timezone is already public.')

        await user_config.set_timezone(user_config.timezone, private=False)
        await ctx.reply('Your timezone is now public.')


def setup(bot: Life) -> None:
    bot.add_cog(Time(bot=bot))
