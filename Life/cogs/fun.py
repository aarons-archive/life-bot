import re
import time

import discord
from discord.ext import commands

from cogs.utilities import exceptions
from cogs.utilities import imaging
from cogs.utilities.imaging import Imaging
from cogs.utilities import utils


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.imaging = Imaging()

    async def get_url(self, ctx: commands.Context, argument: str):

        if not argument:
            argument = ctx.author.name

        try:
            member = await commands.MemberConverter().convert(ctx, str(argument))
            if member.is_avatar_animated() is True:
                argument = str(member.avatar_url_as(format="gif"))
            else:
                argument = str(member.avatar_url_as(format="png"))
        except commands.BadArgument:
            pass

        check_if_url = re.compile("(?:[^:/?#]+):?(?://[^/?#]*)?[^?#]*\.(?:jpg|gif|png|webp|apng|jpeg)(?:\?[^#]*)?(?:#.*)?").match(argument)
        if check_if_url is None:
            raise exceptions.ArgumentError("You provided an invalid argument. Please provide an Image URL or a Members name, id or mention")

        return argument

    async def create_embed(self, image, image_format: str):
        file = discord.File(filename=f"EditedImage.{image_format.lower()}", fp=image)
        embed = discord.Embed(
            colour=discord.Colour.gold(),
        )
        embed.set_image(url=f"attachment://EditedImage.{image_format.lower()}")
        return file, embed

    @commands.command(name="colour", aliases=["color"])
    async def colour(self, ctx, url: str = None, colour: str = None):

        start = time.perf_counter()
        await ctx.trigger_typing()

        if not colour:
            colour = utils.random_colour()

        image_bytes = await imaging.get_image(self.bot, await self.get_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.colourise(image_bytes=image_bytes, image_colour=colour)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Colour: {colour}")
        await ctx.send(file=file, embed=embed)

        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")


def setup(bot):
    bot.add_cog(Fun(bot))
