"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import io
import multiprocessing
import multiprocessing.connection
import sys
from typing import Callable, Optional

import aiohttp
import bs4
import discord
import humanize
import yarl
from wand.color import Color
from wand.image import Image

from core import colours, emojis
from utilities import context, exceptions, utils


def blur(image: Image, area: float = 0, amount: float = 3):
    image.blur(radius=area, sigma=amount)


def adaptive_blur(image: Image, radius: float = 0, sigma: float = 3):

    image.adaptive_blur(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def adaptive_sharpen(image: Image, radius: float = 0, sigma: float = 0):

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def blueshift(image: Image, factor: float = 1.5):

    image.blue_shift(factor=factor)
    return f"Factor: {factor}"


def border(image: Image, colour: str, width: int = 1, height: int = 1):

    with Color(colour) as color:
        image.border(color=color, width=width, height=height, compose="atop")
    return f"Colour: {colour} | Width: {width} | Height: {height}"


def edge(image: Image, radius: float = 0, sigma: float = 1):

    image.canny(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def charcoal(image: Image, radius: float, sigma: float):

    image.charcoal(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def colorize(image: Image, colour = None):

    with Color(colour) as color, Color("rgb(50%, 50%, 50%)") as alpha:
        image.colorize(color=color, alpha=alpha)

    return f"Colour: {colour}"


def despeckle(image: Image):

    image.despeckle()
    return ""


def floor(image: Image):

    image.virtual_pixel = "tile"
    arguments = (
        0,           0,            image.width * 0.2, image.height * 0.5,
        image.width, 0,            image.width * 0.8, image.height * 0.5,
        0,           image.height, image.width * 0.1, image.height,
        image.width, image.height, image.width * 0.9, image.height
    )
    image.distort("perspective", arguments)

    return ""


def emboss(image: Image, radius: float = 0, sigma: float = 0):

    image.transform_colorspace("gray")
    image.emboss(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def enhance(image: Image):

    image.enhance()
    return ""


def flip(image: Image):

    image.flip()
    return None


def flop(image: Image):

    image.flop()
    return None


def frame(image: Image, matte: str, width: int = 10, height: int = 10, inner_bevel: float = 5, outer_bevel: float = 5):

    with Color(matte) as color:
        image.frame(matte=color, width=width, height=height, inner_bevel=inner_bevel, outer_bevel=outer_bevel)

    return f"Colour: {matte} | Width: {width} | Height: {height} | Inner bevel: {inner_bevel} | Outer bevel: {outer_bevel}"


def gaussian_blur(image: Image, radius: float = 0, sigma: float = 0):

    image.gaussian_blur(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def implode(image: Image, amount: float):

    image.implode(amount=amount)
    return f"Amount: {amount}"


def kmeans(image: Image, number_colours: Optional[int] = None):

    image.kmeans(number_colors=number_colours)
    return f"Number of colours: {number_colours}"


def kuwahara(image: Image, radius: float = 1, sigma: Optional[float] = None):

    image.kuwahara(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def motion_blur(image: Image, radius: float = 0, sigma: float = 0, angle: float = 0):

    image.motion_blur(radius=radius, sigma=sigma, angle=angle)
    return f"Radius: {radius} | Sigma: {sigma} | Angle: {angle}"


def negate(image: Image):

    image.negate(channel="rgb")
    return ""


def noise(image: Image, method: str = "uniform", attenuate: float = 1):

    image.noise(method, attenuate=attenuate)
    return f"Method: {method} | Attenuate: {attenuate}"


def oil_paint(image: Image, radius: float = 0, sigma: float = 0):

    image.oil_paint(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def polaroid(image: Image, angle: float = 0, caption = None):

    image.polaroid(angle=angle, caption=caption)
    return f"Angle: {angle} | Caption: {caption}"


def rotate(image: Image, degree: float, reset: bool = True):

    image.rotate(degree=degree, reset_coords=reset)
    return f"Degree: {degree} | Reset: {reset}"


def sepia_tone(image: Image, threshold: float = 0.8):

    image.sepia_tone(threshold=threshold)
    return f"Threshold: {threshold}"


def sharpen(image: Image, radius: float = 0, sigma: float = 0):

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return f"Radius: {radius} | Sigma: {sigma}"


def solarize(image: Image, threshold: float = 0.5):

    image.solarize(threshold=threshold, channel="rgb")
    return f"Threshold: {threshold}"


def spread(image: Image, radius: float):

    image.spread(radius=radius)
    return f"Radius: {radius}"


def swirl(image: Image, degree: float):

    image.swirl(degree=degree)
    return f"Degree: {degree}"


def transparentize(image: Image, transparency: float):

    image.transparentize(transparency=transparency)
    return f"Transparency: {transparency}"


def transpose(image: Image):

    image.transpose()
    return ""


def transverse(image: Image):

    image.transverse()
    return ""


def wave(image: Image):

    image.wave(amplitude=image.height / 32, wave_length=image.width / 4)
    return ""


def cube(image: Image):

    def d3(x: int):
        return int(x / 3)

    image.resize(1000, 1000)
    image.alpha_channel = "opaque"

    top = Image(image)
    top.resize(d3(1000), d3(860))
    top.shear(x=-30, background=Color("none"))
    top.rotate(degree=-30)

    right = Image(image)
    right.resize(d3(1000), d3(860))
    right.shear(background=Color("none"), x=30)
    right.rotate(degree=-30)

    left = Image(image)
    left.resize(d3(1000), d3(860))
    left.shear(background=Color("none"), x=-30)
    left.rotate(degree=30)

    image.resize(width=d3(3000 - 450), height=d3(860 - 100) * 3)
    image.gaussian_blur(sigma=5)

    image.composite(top, left=d3(500 - 250), top=d3(0 - 230) + d3(118))
    image.composite(right, left=d3(1000 - 250) - d3(72), top=d3(860 - 230))
    image.composite(left, left=d3(0 - 250) + d3(68), top=d3(860 - 230))

    top.close()
    right.close()
    left.close()

    image.crop(left=80, top=40, right=665, bottom=710)
    return ""


#


MAX_CONTENT_SIZE = (2 ** 20) * 25
VALID_CONTENT_TYPES = ["image/gif", "image/heic", "image/jpeg", "image/png", "image/webp", "image/avif", "image/svg+xml"]
COMMON_GIF_SITES = ["tenor.com", "giphy.com", "gifer.com"]


async def request_image_bytes(*, session: aiohttp.ClientSession, url: str) -> bytes:

    async with session.get(url) as request:

        if yarl.URL(url).host in COMMON_GIF_SITES:
            page = bs4.BeautifulSoup(await request.text(), features="html.parser")
            if (tag := page.find("meta", property="og:url")) is not None:
                return await request_image_bytes(session=session, url=tag["content"])

        if request.status != 200:
            raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="I was unable to fetch that image. Check the URL or try again later."
            )

        if request.headers.get("Content-Type") not in VALID_CONTENT_TYPES:
            print(request.headers.get("Content-Type"))
            raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="That image format is not allowed, valid formats are **GIF**, **HEIC**, **JPEG**, **PNG**, **WEBP**, **AVIF** and **SVG**."
            )

        if int((request.headers.get("Content-Length") or "0")) > MAX_CONTENT_SIZE:
            raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"That image is too big to edit, maximum file size is **{humanize.naturalsize(MAX_CONTENT_SIZE)}**."
            )

        return await request.read()


async def edit_image(ctx: context.Context, edit_function: Callable[..., None], url: str, **kwargs) -> discord.Embed:

    receiving_pipe, sending_pipe = multiprocessing.Pipe(duplex=False)
    image_bytes = await request_image_bytes(session=ctx.bot.session, url=url)

    process = multiprocessing.Process(target=do_edit_image, daemon=True, args=(edit_function, image_bytes, sending_pipe), kwargs=kwargs)
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, receiving_pipe.recv)
    if isinstance(data, EOFError):
        process.terminate()
        process.close()
        raise exceptions.EmbedError(colour=colours.RED,emoji=emojis.CROSS, description="Something went wrong while trying to edit that image, try again.")

    process.join()

    receiving_pipe.close()
    sending_pipe.close()
    process.terminate()
    process.close()

    url = await utils.upload_file(ctx.bot.session, file_bytes=data[0], file_format=data[1])

    embed = discord.Embed(colour=colours.MAIN)
    embed.set_image(url=url)

    del data

    return embed


def do_edit_image(edit_function: Callable[..., None], image_bytes: bytes, pipe: multiprocessing.connection.Connection, **kwargs):

    try:

        with Image(blob=image_bytes) as image, Color("transparent") as colour:

            image.background_color = colour

            if image.format != "GIF":
                edit_function(image, **kwargs)

            else:
                image.coalesce()
                image.iterator_reset()

                edit_function(image, **kwargs)

                while image.iterator_next():
                    image.background_color = colour
                    edit_function(image, **kwargs)

                image.optimize_transparency()

            edited_image_format = image.format
            edited_image_bytes = image.make_blob()

            pipe.send((edited_image_bytes, edited_image_format))

    except Exception as e:
        print(e, file=sys.stderr)
        pipe.send(ValueError)
