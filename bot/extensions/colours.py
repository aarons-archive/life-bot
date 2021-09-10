# Future
from __future__ import annotations

# Standard Library
import io
import os
from typing import Any, Literal, Optional

# Packages
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# My stuff
from core import colours, emojis
from core.bot import Life
from utilities import context, decorators, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Colours(bot=bot))


Modes = Literal["monochrome", "monochrome-dark", "monochrome-light", "analogic", "complement", "analogic-complement", "triad", "quad"]
KABEL_BLACK_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/fonts/kabel_black.otf"))


class Colours(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @decorators.async_executor
    def generate_colour_square(self, colour: str) -> Any:

        with Image.new(mode="RGBA", size=(256, 100), color=colour) as image:

            buffer = io.BytesIO()
            image.save(buffer, "png")

        buffer.seek(0)
        return buffer

    @decorators.async_executor
    def generate_colour_scheme(self, hex_codes: list[str], names: list[str]) -> Any:

        with Image.new(mode="RGBA", size=(200 * len(hex_codes), 225), color="white") as image:

            draw = ImageDraw.Draw(im=image)
            x = 0

            for hex_code, name in zip(hex_codes, names):

                draw.rectangle(xy=((x, 25), (x + 200, 225)), fill=hex_code)
                draw.text(xy=(x + 5, 5), text=name, font=ImageFont.truetype(font=KABEL_BLACK_FONT, size=20), fill="#1F1E1C")
                draw.text(xy=(x + 5, 30), text=hex_code, font=ImageFont.truetype(font=KABEL_BLACK_FONT, size=20), fill="#1F1E1C")

                x += 200

            buffer = io.BytesIO()
            image.save(buffer, "png")

        buffer.seek(0)
        return buffer

    @commands.command(name="randomcolour", aliases=["random-colour", "random_colour", "randomcolor", "random-color", "random_color", "rc"])
    async def randomcolour(self, ctx: context.Context) -> None:

        async with self.bot.session.get(url=f"https://www.thecolorapi.com/id", params={"hex": utils.random_hex().strip("#")}) as request:

            if request.status != 200:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="Information about that colour is unavailable."
                )

            data = await request.json()

            hex = data["hex"]["value"]
            rgb = data["rgb"]["value"]
            r, g, b = data["rgb"]["r"], data["rgb"]["g"], data["rgb"]["b"]
            hsl = data["hsl"]["value"]
            hsv = data["hsv"]["value"]
            cmyk = data["cmyk"]["value"]
            xyz = data["XYZ"]["value"]

            name = data["name"]["value"]
            name_is_exact_match = data["name"]["exact_match_name"]
            name_exact_match_hex = data["name"]["closest_named_hex"]

        buffer = await self.generate_colour_square(hex)
        url = await utils.upload_file(session=self.bot.session, file_bytes=buffer, file_format="png")
        buffer.close()

        embed = discord.Embed(
            title=f"{name} - {hex}",
            description=f"**Hex:** {hex}\n"
                        f"**RGB:** {rgb}\n"
                        f"**HSL:** {hsl}\n"
                        f"**HSV:** {hsv}\n"
                        f"**XYZ:** {xyz.lower()}\n"
                        f"**CMYK:** {cmyk}\n",
            colour=discord.Colour.from_rgb(r, g, b),
        ).set_image(
            url=url
        )

        if name_is_exact_match is False:
            embed.set_footer(text=f"{name}'s exact hex code is {name_exact_match_hex}.")

        await ctx.reply(embed=embed)

    @commands.command(name="colourscheme", aliases=["colour-scheme", "colour_scheme", "colorscheme", "color-scheme", "color_scheme", "cs"])
    async def colourscheme(
        self,
        ctx: context.Context,
        seed: Optional[discord.Color] = utils.MISSING,
        mode: Optional[Modes] = "monochrome",
        count: int = utils.MISSING,
    ) -> None:

        count = count or 5

        if count > 20:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Max colour count is **20**."
            )

        seed = seed or discord.Colour.random()

        async with self.bot.session.get(url=f"https://www.thecolorapi.com/scheme", params={"hex": str(seed), "mode": mode, "count": count}) as request:

            if request.status != 200:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="Information about that colour is unavailable."
                )

            data = await request.json()

            hex_codes = [colour["hex"]["value"] for colour in data["colors"]]
            names = [colour["name"]["value"] for colour in data["colors"]]

        buffer = await self.generate_colour_scheme(hex_codes, names)
        url = await utils.upload_file(session=self.bot.session, file_bytes=buffer, file_format="png")
        buffer.close()

        embed = discord.Embed(
            description=f"**Base:** {seed}\n"
                        f"**Mode:** {mode}\n"
                        f"**Count:** {count}\n"
                        f"**Link:** [click here]({url})",
            colour=seed,
        ).set_image(url=url)

        await ctx.reply(embed=embed)
