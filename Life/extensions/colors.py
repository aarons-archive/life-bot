import randomcolor
import webcolors
import typing
from io import BytesIO
from PIL import Image

import discord
from discord.ext import commands

from core.bot import Life
from core import colours, emojis
from utilities import decorators, context, exceptions

def setup(bot: Life) -> None:
  bot.add_cog(Colors(bot=bot))

class Colors(commands.Cog) -> None:
  
  def __init__(self, bot: Life):
    self.bot = bot
    
    @AsyncExecutor
    def generate_colour(self, colour: tuple):
        image = Image.new("RGB", (256, 100), colour)

        buffer = BytesIO()
        image.save(buffer, "png")
        image.close()

        buffer.seek(0)

        return buffer

    @AsyncExecutor
    def closest_colour(self, requested_colour):
        min_colours = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]
    
    @commands.command(name="random-color", aliases=["randomcolor", "random-colour", "randomcolour"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomcolor_command(self, ctx: context.Context, hue: typing.Optional[typing.Literal["pink", "purple", "green", "blue", "yellow", "orange", "red"]):
        """
        Generate a random color.

        `Hue` can be: `pink`, `purple`, `green`, `blue`, `yellow`, `orange` or `red`
        """

        hex = randomcolor.RandomColor().generate(
            hue=hue or None)[0].lstrip("#")
        rgb = webcolors.hex_to_rgb("#" + hex)

        file = discord.File(
            fp=await self.generate_colour(color=rgb), filename=f"Life_{hex}.png"
        )
        embed = discord.Embed(
            description=f"**Name:** {str(await self.closest_colour(rgb)).capitalize()}\n**Hex:** #{hex}\n**Rgb:** {rgb}",
            color=discord.Color.from_rgb(r=rgb[0], g=rgb[1], b=rgb[2]),
        )
        embed.set_image(url=f"attachment://Life_{hex}.png")

        await ctx.reply(file=file, embed=embed)
