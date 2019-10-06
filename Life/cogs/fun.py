from discord.ext import commands
from .utilities import imaging
import discord
import typing
import random
import time
import re


class Fun(commands.Cog):
    """
    Fun commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="colour")
    async def colour(self, ctx, *, image: typing.Union[discord.Member, str] = None):
        """
        Coverts an image into a two tone image with a random colour.

        This command only really works for image with a few colours, images with only 1 colour or image with over 50 may not work correctly.

        `image`: This can be an image attachment, discord member or a url.
        """
        if not image:
            image = ctx.author

        # Start typing and timer.
        start = time.perf_counter()
        await ctx.trigger_typing()

        # If the user attached an image.
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url

            # If the attachemnts url does not end in .png or .jpeg
            if not url.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

            # Get the users avatar
            image_bytes = await imaging.get_image(self.bot, url)
            # Create image with PIL
            image_colour = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (66, 66, 66))
            # Send image.
            await ctx.send(content=f"Here is your randomly coloured image.", file=discord.File(filename=f"ImageColour.png", fp=image_colour))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

        # If the image is user
        if isinstance(image, discord.Member):
            # Get the users avatar
            avatar_bytes = await imaging.get_image(self.bot, str(image.avatar_url_as(size=1024, format="png")))
            # Create image with PIL
            avatar_colour = await self.bot.loop.run_in_executor(None, imaging.colour, avatar_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (66, 66, 66))
            # Send image.
            await ctx.send(content=f"Here is your randomly coloured image.", file=discord.File(filename=f"ImageColour.png", fp=avatar_colour))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

        # Else, it was just a regular string.
        re_url = re.compile("https?://(?:www\.)?.+/?")
        check = re_url.match(image)
        if check is False:
            return await ctx.send("That was not a valid URL.")

        # If the url does not end in .png or .jpeg
        if not image.endswith((".jpg", ".jpeg", ".png")):
            return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

        # Get the users avatar
        image_bytes = await imaging.get_image(self.bot, image)
        # Create image with PIL
        image_colour = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (66, 66, 66))
        # Send image.
        await ctx.send(content=f"Here is your randomly coloured image.", file=discord.File(filename=f"ImageColour.png", fp=image_colour))
        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="halloween")
    async def halloween(self, ctx, *, image: typing.Union[discord.Member, str] = None):
        """
        Coverts an image into a two tone image with an orange halloween colour.

        This command only really works for image with a few colours, images with only 1 colour or image with over 50 may not work correctly.

        `image`: This can be an image attachment, discord member or a url.
        """
        if not image:
            image = ctx.author

        # Start typing and timer.
        start = time.perf_counter()
        await ctx.trigger_typing()

        # If the user attached an image.
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url

            # If the attachemnts url does not end in .png or .jpeg
            if not url.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

            # Get the users avatar
            image_bytes = await imaging.get_image(self.bot, url)
            # Create image with PIL
            image_colour = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (255, 127, 0), (66, 66, 66))
            # Send image.
            await ctx.send(content=f"Here is your spooky image.", file=discord.File(filename=f"ImageColour.png", fp=image_colour))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

        # If the image is user
        if isinstance(image, discord.Member):
            # Get the users avatar
            avatar_bytes = await imaging.get_image(self.bot, str(image.avatar_url_as(size=1024, format="png")))
            # Create image with PIL
            avatar_colour = await self.bot.loop.run_in_executor(None, imaging.colour, avatar_bytes, (255, 127, 0), (66, 66, 66))
            # Send image.
            await ctx.send(content=f"Here is your spooky image.", file=discord.File(filename=f"ImageColour.png", fp=avatar_colour))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

        # Else, it was just a regular string.
        re_url = re.compile("https?://(?:www\.)?.+/?")
        check = re_url.match(image)
        if check is False:
            return await ctx.send("That was not a valid URL.")

        # If the url does not end in .png or .jpeg
        if not image.endswith((".jpg", ".jpeg", ".png")):
            return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

        # Get the users avatar
        image_bytes = await imaging.get_image(self.bot, image)
        # Create image with PIL
        image_colour = await self.bot.loop.run_in_executor(None, imaging.colour, image_bytes, (255, 127, 0), (66, 66, 66))
        # Send image.
        await ctx.send(content=f"Here is your spooky image.", file=discord.File(filename=f"ImageColour.png", fp=image_colour))
        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="test")
    async def test(self, ctx):
        image_bytes = await imaging.get_image(self.bot, str(ctx.author.avatar_url_as(size=128, format="png")))

        image = await self.bot.loop.run_in_executor(None, imaging.gif, image_bytes)

        await ctx.send(content=f"Here is your test image.", file=discord.File(filename=f"ImageColour.gif", fp=image))


def setup(bot):
    bot.add_cog(Fun(bot))
