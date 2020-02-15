import random
import re
import time
import typing

import discord
from discord.ext import commands

from utilities import imaging


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="colour", aliases=["color"])
    async def colour(self, ctx, *, image: typing.Union[discord.Member, str] = None):
        """
        Get a randomly coloured image of the users choice.

        `image`: A discord member (mention, id, name), URL or attachment.
        """

        if not image:
            image = ctx.author

        start = time.perf_counter()
        await ctx.trigger_typing()

        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
            if not url.endswith((".jpg", ".jpeg", ".png", ".gif", ".wepb")):
                return await ctx.send("That was not a valid attachment. It must be a PNG, JPEG or WEBP image.")

        elif isinstance(image, discord.Member):
            url = str(image.avatar_url_as(format="png"))

        else:
            url = image

            check_link = re.compile("https?://(?:www\.)?.+/?").match(url)
            if check_link is False:
                return await ctx.send("That was not a valid URL.")

            if not url.endswith((".jpg", ".jpeg", ".png", ".gif", ".wepb")):
                return await ctx.send("That was not a valid url. It must be a PNG, JPEG or WEBP image.")

        image_bytes = await imaging.get_image(self.bot, url)

        image = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        file = discord.File(filename=f"RandomColourImage.png", fp=image)

        embed = discord.Embed(
            colour=discord.Colour.gold(),
            title="Here is your randomly coloured image."
        )
        embed.set_image(url=f"attachment://RandomColourImage.png")

        await ctx.send(file=file, embed=embed)

        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")


def setup(bot):
    bot.add_cog(Fun(bot))
