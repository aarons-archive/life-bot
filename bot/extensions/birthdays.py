# Future
from __future__ import annotations

# Packages
import discord
import pendulum
from discord.ext import commands

# My stuff
from core import colours, emojis
from core.bot import Life
from utilities import context, converters, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Birthdays(bot=bot))


class Birthdays(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name="birthday", aliases=["bd"], invoke_without_command=True)
    async def _birthday(self, ctx: context.Context[Life], *, person: discord.Member = utils.MISSING) -> None:
        """
        Display yours or another person's birthday.

        **person**: The person to display the birthday of. Can be their ID, Username, Nickname or @Mention, If not provided than your birthday will be displayed.
        """

        member = person or ctx.author
        user_config = await self.bot.user_manager.get_config(member.id)

        if not user_config.birthday:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{member.mention}** has not set their birthday."
            )
        if user_config.birthday_private and ctx.author.id != member.id:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{member.mention}** has their birthday set as private.",
            )

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"Birthday information for {member}:",
            description=f"**Birthday:** {utils.format_date(user_config.birthday)}\n"
                        f"**Next birthday date:** {utils.format_date(user_config.next_birthday)}\n"
                        f"**Next birthday:** In {utils.format_difference(user_config.next_birthday)}\n"
                        f"**Age:** {user_config.age}\n",
        )
        await ctx.reply(embed=embed)

    @_birthday.command(name="set")
    async def _birthday_set(self, ctx: context.Context[Life], *, date: converters.DatetimeConverter) -> None:
        """
        Sets your birthday.

        **date**: Your birthday. This should include some form of date such as **tomorrow**, **in 3 weeks** or **1st january 2020**.
        """

        entries = {index: (phrase, datetime) for index, (phrase, datetime) in enumerate(date[1].items())}

        choice = await ctx.choice(
            entries=[f"`{index + 1}:` {phrase}\n{utils.format_date(datetime)}" for index, (phrase, datetime) in entries.items()],
            per_page=5,
            splitter="\n\n",
            title="Type the number of the date you want to set your birthday too:",
        )
        _, birthday = entries[choice]

        if birthday > pendulum.now(tz="UTC").subtract(years=13):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Your birthday must allow you to be more than 13 years old.",
            )

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        await user_config.set_birthday(birthday)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Birthday set to **{utils.format_date(user_config.birthday)}**",
        )
        await ctx.reply(embed=embed)

    @_birthday.command(name="reset")
    async def _birthday_reset(self, ctx: context.Context[Life]) -> None:
        """
        Resets your birthday.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        await user_config.set_birthday()

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="Birthday reset."
            )
        )

    @_birthday.command(name="private")
    async def _birthday_private(self, ctx: context.Context[Life]) -> None:
        """
        Makes your birthday private.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)

        if user_config.birthday_private is True:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Your birthday is already **private**."
            )

        await user_config.set_birthday(user_config.birthday, private=True)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="Your birthday is now **private**."
            )
        )

    @_birthday.command(name="public")
    async def _birthday_public(self, ctx: context.Context[Life]) -> None:
        """
        Makes your birthday public.
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)

        if user_config.birthday_private is False:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Your birthday is already **public**."
            )

        await user_config.set_birthday(user_config.birthday, private=False)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="Your birthday is now **public**."
            )
        )

    @commands.guild_only()
    @_birthday.command(name="list", aliases=["upcoming"])
    async def _birthday_list(self, ctx: context.Context[Life]) -> None:
        """
        Displays a list of upcoming birthdays in the current server.
        """

        if not (birthdays := await self.bot.user_manager.birthdays(guild_id=ctx.guild.id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their birthday, or everyone has set them to be private.",
            )

        await ctx.paginate_embed(
            entries=[
                f"{member.mention}:\n"
                f"**Birthday:** {utils.format_date(birthday)}\n"
                f"**Next birthday date:** {utils.format_date(next_birthday)}\n"
                f"**Next birthday:** In {utils.format_difference(next_birthday)}\n"
                f"**Age:** {age}"
                for member, birthday, age, next_birthday in birthdays
            ],
            per_page=3,
            splitter="\n\n",
            title=f"Upcoming birthdays in **{ctx.guild}**:",
        )

    @commands.guild_only()
    @_birthday.command(name="next")
    async def _birthday_next(self, ctx: context.Context[Life]) -> None:
        """
        Displays the next person to have a birthday in the current server.
        """

        if not (birthdays := await self.bot.user_manager.birthdays(guild_id=ctx.guild.id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No one has set their birthday, or everyone has set them to be private.",
            )

        member, birthday, age, next_birthday = birthdays[0]

        await ctx.reply(
            embed=utils.embed(
                title=f"Birthday information for {member}:",
                description=f"**Birthday:** {utils.format_date(birthday)}\n"
                            f"**Next birthday date:** {utils.format_date(next_birthday)}\n"
                            f"**Next birthday:** In {utils.format_difference(next_birthday)}\n"
                            f"**Age:** {age}\n",
            )
        )

    @commands.guild_only()
    @_birthday.command(name="card")
    async def _birthday_card(self, ctx: context.Context[Life]) -> None:
        """
        Creates an image with the birthday month of all servers members.
        """

        async with ctx.typing():
            file = await self.bot.user_manager.create_birthday_card(guild_id=ctx.guild.id)
            await ctx.reply(file=file)

    # Aliases

    @commands.command(name="birthdays")
    async def _birthdays(self, ctx: context.Context[Life]) -> None:
        """
        Displays a list of upcoming birthdays in the current server.
        """

        await ctx.invoke(self._birthday_upcoming)  # type: ignore
