import random
import re
import time
import typing

import discord
from discord.ext import commands

from .utilities import imaging


class Fun(commands.Cog):
    """
    Fun commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def do_colour(self, ctx, url):

        # Start timer.
        start = time.perf_counter()

        # Get the image bytes.
        image_bytes = await imaging.get_image(self.bot, url)

        image = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        await ctx.send(content=f"Here is your randomly coloured image.", file=discord.File(filename=f"Image.png", fp=image))

        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="colour")
    async def colour(self, ctx, *, image: typing.Union[discord.Member, str] = None):

        if not image:
            image = ctx.author
        # Start typing.
        await ctx.trigger_typing()
        # If the user attached an image.
        if ctx.message.attachments:
            # Get the url of the attachment.
            url = ctx.message.attachments[0].url
            # If the attachemnts url is not a valid image
            if not url.endswith((".jpg", ".jpeg", ".png", ".gif", ".wepb")):
                return await ctx.send("That was not a valid attachment. It must be a PNG, JPEG, WEBP or GIF image.")

        # If the image is a user.
        elif isinstance(image, discord.Member):
            url = str(image.avatar_url_as(format="png"))

        # Else, it was just a regular string.
        else:
            url = image
            # Check if the users input is a link.
            check_link = re.compile("https?://(?:www\.)?.+/?").match(url)
            if check_link is False:
                return await ctx.send("That was not a valid URL.")
            # If the url is not a valid image.
            if not url.endswith((".jpg", ".jpeg", ".png", ".gif", ".wepb")):
                return await ctx.send("That was not a valid url. It must be a PNG, JPEG, WEBP or GIF image.")

        # Start timer.
        start = time.perf_counter()
        # Get the image bytes.
        image_bytes = await imaging.get_image(self.bot, url)
        # Create the image.
        image = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        await ctx.send(content=f"Here is your randomly coloured image.", file=discord.File(filename=f"Image.png", fp=image))
        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")


def setup(bot):
    bot.add_cog(Fun(bot))
