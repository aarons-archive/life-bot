import re
import time
import typing

import discord
from discord.ext import commands

from cogs.utilities import exceptions
from cogs.utilities import imaging
from cogs.utilities import utils


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_url(self, ctx: commands.Context, argument: str):

        if not argument:
            argument = ctx.author.name

        try:
            member = await commands.MemberConverter().convert(ctx, str(argument))
            argument = str(member.avatar_url_as(format="png"))
        except commands.BadArgument:
            pass

        check_if_url = re.compile("(?:[^:/?#]+):?(?://[^/?#]*)?[^?#]*\.(?:jpg|gif|png|webp|apng|jpeg)(?:\?[^#]*)?(?:#.*)?").match(argument)
        if check_if_url is None:
            raise exceptions.ArgumentError("You provided an invalid argument. Please provide an Image URL or a Members name, id or mention")

        return argument

    @commands.command(name="colour", aliases=["color"])
    async def colour(self, ctx, url: typing.Optional[str] = None, colour: str = None):

        start = time.perf_counter()
        await ctx.trigger_typing()

        if not colour:
            colour = utils.random_colour()

        url = await self.get_url(ctx=ctx, argument=url)
        image_bytes = await imaging.get_image(self.bot, url)
        image = imaging.colour(image_bytes=image_bytes, image_colour=colour)

        file = discord.File(filename=f"ColourImage.png", fp=image)
        embed = discord.Embed(
            colour=discord.Colour.gold(),
        )
        embed.set_image(url=f"attachment://ColourImage.png")
        embed.set_footer(text=f"Colour: {colour}")
        await ctx.send(file=file, embed=embed)

        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="charcoal")
    async def charcoal(self, ctx, url: typing.Optional[str] = None, radius: float = 1.5, sigma: float = 0.5):

        start = time.perf_counter()
        await ctx.trigger_typing()

        url = await self.get_url(ctx=ctx, argument=url)
        image_bytes = await imaging.get_image(self.bot, url)
        image = imaging.charcoal(image_bytes=image_bytes, radius=radius, sigma=sigma)

        file = discord.File(filename=f"Charcoal.png", fp=image)
        embed = discord.Embed(
            colour=discord.Colour.gold(),
        )
        embed.set_image(url=f"attachment://Charcoal.png")
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma}")

        await ctx.send(file=file, embed=embed)

        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="implode")
    async def implode(self, ctx, url: typing.Optional[str] = None, amount: float = 0.35):

        start = time.perf_counter()
        await ctx.trigger_typing()

        url = await self.get_url(ctx=ctx, argument=url)
        image_bytes = await imaging.get_image(self.bot, url)
        image = imaging.implode(image_bytes=image_bytes, amount=amount)

        file = discord.File(filename=f"ImplodeImage.png", fp=image)
        embed = discord.Embed(
            colour=discord.Colour.gold(),
        )
        embed.set_image(url=f"attachment://ImplodeImage.png")
        embed.set_footer(text=f"Amount: {amount}")
        await ctx.send(file=file, embed=embed)

        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")


def setup(bot):
    bot.add_cog(Fun(bot))
