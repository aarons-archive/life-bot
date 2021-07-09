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

import multiprocessing
import multiprocessing.connection
import os
import os.path
import subprocess
import sys
from typing import Any, Callable, Literal, Optional

import aiohttp
import bs4
import discord
import humanize
import yarl
from wand.color import Color
from wand.image import Image

from core import colours, emojis
from utilities import context, exceptions, utils

if sys.platform == "win32":
    CMD = f"bash"
else:
    CMD = f"{os.getenv('SHELL') or '/bin/bash'}"


def blur(image: Image, area: float = 0, amount: float = 3) -> None:
    image.blur(radius=area, sigma=amount)


def adaptive_blur(image: Image, radius: float = 0, sigma: float = 3) -> None:
    image.adaptive_blur(radius=radius, sigma=sigma)


def adaptive_sharpen(image: Image, radius: float = 0, sigma: float = 0) -> None:
    image.adaptive_sharpen(radius=radius, sigma=sigma)


def blueshift(image: Image, factor: float = 1.5) -> None:
    image.blue_shift(factor=factor)


def border(image: Image, colour: str, width: int = 1, height: int = 1) -> None:
    with Color(colour) as color:
        image.border(color=color, width=width, height=height, compose="atop")


def edge(image: Image, radius: float = 0, sigma: float = 1) -> None:
    image.canny(radius=radius, sigma=sigma)


def charcoal(image: Image, radius: float, sigma: float) -> None:
    image.charcoal(radius=radius, sigma=sigma)


def colorize(image: Image, colour=None) -> None:
    with Color(colour) as color, Color("rgb(50%, 50%, 50%)") as alpha:
        image.colorize(color=color, alpha=alpha)


def despeckle(image: Image) -> None:
    image.despeckle()


def floor(image: Image) -> None:
    image.virtual_pixel = "tile"
    image.distort(
            "perspective",
            (
                0, 0, image.width * 0.2, image.height * 0.5,
                image.width, 0, image.width * 0.8, image.height * 0.5,
                0, image.height, image.width * 0.1, image.height,
                image.width, image.height, image.width * 0.9, image.height
            )
    )


def emboss(image: Image, radius: float = 0, sigma: float = 0) -> None:
    image.transform_colorspace("gray")
    image.emboss(radius=radius, sigma=sigma)


def enhance(image: Image) -> None:
    image.enhance()


def flip(image: Image) -> None:
    image.flip()


def flop(image: Image) -> None:
    image.flop()


def frame(image: Image, matte: str, width: int = 10, height: int = 10, inner_bevel: float = 5, outer_bevel: float = 5) -> None:
    with Color(matte) as color:
        image.frame(matte=color, width=width, height=height, inner_bevel=inner_bevel, outer_bevel=outer_bevel)


def gaussian_blur(image: Image, radius: float = 0, sigma: float = 0) -> None:
    image.gaussian_blur(radius=radius, sigma=sigma)


def implode(image: Image, amount: float) -> None:
    image.implode(amount=amount)


def kmeans(image: Image, number_colours: Optional[int] = None) -> None:
    image.kmeans(number_colors=number_colours)


def kuwahara(image: Image, radius: float = 1, sigma: Optional[float] = None) -> None:
    image.kuwahara(radius=radius, sigma=sigma)


def motion_blur(image: Image, radius: float = 0, sigma: float = 0, angle: float = 0) -> None:
    image.motion_blur(radius=radius, sigma=sigma, angle=angle)


def negate(image: Image) -> None:
    image.negate(channel="rgb")


def noise(image: Image, method: str = "uniform", attenuate: float = 1) -> None:
    image.noise(method, attenuate=attenuate)


def oil_paint(image: Image, radius: float = 0, sigma: float = 0) -> None:
    image.oil_paint(radius=radius, sigma=sigma)


def polaroid(image: Image, angle: float = 0, caption=None) -> None:
    image.polaroid(angle=angle, caption=caption)


def rotate(image: Image, degree: float, reset: bool = True) -> None:
    image.rotate(degree=degree, reset_coords=reset)


def sepia_tone(image: Image, threshold: float = 0.8) -> None:
    image.sepia_tone(threshold=threshold)


def sharpen(image: Image, radius: float = 0, sigma: float = 0) -> None:
    image.adaptive_sharpen(radius=radius, sigma=sigma)


def solarize(image: Image, threshold: float = 0.5) -> None:
    image.solarize(threshold=threshold, channel="rgb")


def spread(image: Image, radius: float) -> None:
    image.spread(radius=radius)


def swirl(image: Image, degree: float) -> None:
    image.swirl(degree=degree)


def transparentize(image: Image, transparency: float) -> None:
    image.transparentize(transparency=transparency)


def transpose(image: Image) -> None:
    image.transpose()


def transverse(image: Image) -> None:
    image.transverse()


def wave(image: Image) -> None:
    image.wave(amplitude=image.height / 32, wave_length=image.width / 4)


def cube(image: Image, filename: str) -> Image:

    image.resize(width=1000, height=1000)

    PATH = os.path.join(os.path.abspath(os.getcwd()), os.path.abspath(f"resources/cube/{filename}"))
    image.save(filename=f"{PATH}.png")

    COMMAND = r"""
    convert \
        \( ./resources/cube/{filename}.png -alpha set -virtual-pixel transparent +distort Affine "0,1000 0,0  0,0 -200,-100  1000,1000 200,-100" \) \
        \( ./resources/cube/{filename}.png -alpha set -virtual-pixel transparent -resize 1000x1000 +distort Affine "1000,0 0,0  0,0 -200,-100  1000,1000 0,200" \) \
        \( ./resources/cube/{filename}.png -alpha set -virtual-pixel transparent -resize 1000x1000 +distort Affine "0,0 0,0  0,1000 0,200  1000,0 200,-100" \) \
        \
        -background none -compose plus -layers merge +repage -compose over ./resources/cube/{filename}_edited.png
    """.format(filename=filename)

    subprocess.run(f"{CMD} -c {COMMAND}", cwd=os.getcwd())
    return Image(filename=f"{PATH}_edited.png")


def sphere(image: Image, filename: str) -> Image:

    image.colorize(Color("transparent"), alpha=Color("rgb(1%, 1%, 1%)"))  # Necessary because the spherize script doesn't like colourless images??
    image.resize(width=1000, height=1000)

    PATH = os.path.join(os.path.abspath(os.getcwd()), os.path.abspath(f"resources/sphere/{filename}"))
    image.save(filename=f"{PATH}.png")

    COMMAND = r"./sphere.sh -a 1.1 -b none -s -t resources/sphere/{filename}.png resources/sphere/{filename}_edited.png".format(filename=filename)

    subprocess.run(f"{CMD} {COMMAND}", cwd=os.getcwd())
    return Image(filename=f"{PATH}_edited.png")


def tshirt(image: Image, filename: str) -> Image:

    PATH = os.path.join(os.path.abspath(os.getcwd()), os.path.abspath(f"resources/tshirt/{filename}"))
    image.save(filename=f"{PATH}.png")

    COMMAND = r"./tshirt.sh -r '130x130+275+175' -R -3 -o 5,0 lighting.png displace.png resources/tshirt/{filename}.png tshirt_gray.png resources/tshirt/{filename}_edited.png".format(filename=filename)

    subprocess.run(f"{CMD} {COMMAND}", cwd=os.getcwd())
    return Image(filename=f"{PATH}_edited.png")


def pixel(image: Image, filename: str, method: Literal["square", "s", "hexagon", "h", "random", "r"]) -> Image:

    image.resize(width=1000, height=1000)

    PATH = os.path.join(os.path.abspath(os.getcwd()), os.path.abspath(f"resources/pixel/{filename}"))
    image.save(filename=f"{PATH}.png")

    COMMAND = r"./pixel.sh -k {method} -t 0 -b 150 resources/pixel/{filename}.png resources/pixel/{filename}_edited.png".format(filename=filename, method=method)

    subprocess.run(f"{CMD} {COMMAND}", cwd=os.getcwd())
    return Image(filename=f"{PATH}_edited.png")


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


async def edit_image(ctx: context.Context, edit_function: Callable[..., Any], url: str, **kwargs) -> discord.Embed:
    receiving_pipe, sending_pipe = multiprocessing.Pipe(duplex=False)
    image_bytes = await request_image_bytes(session=ctx.bot.session, url=url)

    process = multiprocessing.Process(target=do_edit_image, daemon=True, args=(edit_function, image_bytes, sending_pipe), kwargs=kwargs)
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, receiving_pipe.recv)
    if isinstance(data, EOFError):
        process.terminate()
        process.close()
        raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Something went wrong while trying to edit that image, try again.")

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


def do_edit_image(edit_function: Callable[..., Any], image_bytes: bytes, pipe: multiprocessing.connection.Connection, **kwargs) -> None:
    try:

        with Image(blob=image_bytes) as image, Color("transparent") as colour:

            if edit_function in {cube, sphere, tshirt, pixel}:

                if image.format != "GIF":
                    image = edit_function(image, **kwargs)

                else:
                    image.coalesce()
                    for index, x in enumerate(image.sequence):
                        image.sequence[index] = edit_function(Image(x), **kwargs)
                    image.format = "GIF"
                    image.optimize_transparency()

            elif image.format != "GIF":
                image.background_color = colour
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
