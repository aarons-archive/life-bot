# Future
from __future__ import annotations

# Standard Library
import multiprocessing
import sys
from multiprocessing.connection import Connection
from typing import Any, Callable, Literal

# Packages
import aiohttp
import bs4
import humanize
import yarl
from wand.color import Color
from wand.image import Image

# My stuff
from core import colours, emojis
from utilities import custom, exceptions, objects, utils


PixelInterpolateMethods = Literal[
    "undefined",
    "average",
    "average9",
    "average16",
    "background",
    "bilinear",
    "blend",
    "catrom",
    "integer",
    "mesh",
    "nearest",
    "spline",
]
NoiseTypes = Literal[
    "undefined",
    "uniform",
    "gaussian",
    "multiplicative_gaussian",
    "impulse",
    "laplacian",
    "poisson",
    "random"
]


def blur(image: Image, radius: float, sigma: float) -> None:
    image.blur(radius=radius, sigma=sigma)


def adaptive_blur(image: Image, radius: float, sigma: float) -> None:
    image.adaptive_blur(radius=radius, sigma=sigma)


def sharpen(image: Image, radius: float, sigma: float) -> None:
    image.adaptive_sharpen(radius=radius, sigma=sigma)


def adaptive_sharpen(image: Image, radius: float, sigma: float) -> None:
    image.adaptive_sharpen(radius=radius, sigma=sigma)


def blueshift(image: Image, factor: float) -> None:
    image.blue_shift(factor=factor)


def border(image: Image, colour: str, width: int, height: int) -> None:

    with Color(colour) as color:
        image.border(color=color, width=width, height=height, compose="atop")


def colorize(image: Image, colour: str) -> None:

    with Color(colour) as color, Color("rgb(50%, 50%, 50%)") as alpha:
        image.colorize(color=color, alpha=alpha)


def despeckle(image: Image) -> None:
    image.despeckle()


def floor(image: Image) -> None:

    image.virtual_pixel = "tile"
    image.distort(
        method="perspective",
        arguments=(
            0, 0, image.width * 0.2, image.height * 0.5,
            image.width, 0, image.width * 0.8, image.height * 0.5,
            0, image.height, image.width * 0.1, image.height,
            image.width, image.height, image.width * 0.9, image.height
        )
    )


def emboss(image: Image, radius: float, sigma: float) -> None:

    image.transform_colorspace("gray")
    image.emboss(radius=radius, sigma=sigma)


def enhance(image: Image) -> None:
    image.enhance()


def flip(image: Image) -> None:
    image.flip()


def flop(image: Image) -> None:
    image.flop()


def frame(image: Image, matte: str, width: int, height: int, inner_bevel: float, outer_bevel: float) -> None:

    with Color(matte) as color:
        image.frame(matte=color, width=width, height=height, inner_bevel=inner_bevel, outer_bevel=outer_bevel, compose="atop")


def implode(image: Image, amount: float, method: PixelInterpolateMethods) -> None:
    image.implode(amount=amount, method=method)


def kmeans(image: Image, number_colours: int) -> None:
    image.kmeans(number_colors=number_colours)


def kuwahara(image: Image, radius: float, sigma: float) -> None:
    image.kuwahara(radius=radius, sigma=sigma)


def motion_blur(image: Image, radius: float, sigma: float, angle: float) -> None:
    image.motion_blur(radius=radius, sigma=sigma, angle=angle)


def negate(image: Image) -> None:
    image.negate(channel="rgb")


def noise(image: Image, noise_type: NoiseTypes, attenuate: float) -> None:
    image.noise(noise_type=noise_type, attenuate=attenuate)


def oil_paint(image: Image, radius: float, sigma: float) -> None:
    image.oil_paint(radius=radius, sigma=sigma)


def polaroid(image: Image, angle: float, caption: str, method: PixelInterpolateMethods) -> None:
    image.polaroid(angle=angle, caption=caption, method=method)


def rotate(image: Image, degree: float, reset_coords: bool) -> None:
    image.rotate(degree=degree, reset_coords=reset_coords)


def sepia_tone(image: Image, threshold: float) -> None:
    image.sepia_tone(threshold=threshold)


def solarize(image: Image, threshold: float) -> None:
    image.solarize(threshold=threshold, channel="rgb")


def spread(image: Image, radius: float, method: PixelInterpolateMethods) -> None:
    image.spread(radius=radius, method=method)


def swirl(image: Image, degree: float, method: PixelInterpolateMethods) -> None:
    image.swirl(degree=degree, method=method)


def transparentize(image: Image, transparency: float) -> None:
    image.transparentize(transparency=transparency)


def wave(image: Image, method: PixelInterpolateMethods) -> None:
    image.wave(amplitude=image.height / 32, wave_length=image.width / 5, method=method)


#


MAX_CONTENT_SIZE = (2 ** 20) * 25
VALID_CONTENT_TYPES = ["image/gif", "image/heic", "image/jpeg", "image/png", "image/webp", "image/avif", "image/svg+xml"]
COMMON_GIF_SITES = ["tenor.com", "giphy.com", "gifer.com"]


async def request_image_bytes(*, session: aiohttp.ClientSession, url: str) -> bytes:

    async with session.get(url) as request:

        if yarl.URL(url).host in COMMON_GIF_SITES:
            page = bs4.BeautifulSoup(await request.text(), features="html.parser")
            tag: Any = page.find("meta", property="og:url")
            if tag:
                return await request_image_bytes(session=session, url=tag.content)

        if request.status != 200:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="I was unable to fetch that image. Check the URL or try again later.",
            )

        if request.headers.get("Content-Type") not in VALID_CONTENT_TYPES:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="That image format is not allowed, valid formats are **GIF**, **HEIC**, **JPEG**, **PNG**, **WEBP**, **AVIF** and **SVG**.",
            )

        if int(request.headers.get("Content-Length") or "0") > MAX_CONTENT_SIZE:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That image is too big to edit, maximum file size is **{humanize.naturalsize(MAX_CONTENT_SIZE)}**.",
            )

        return await request.read()


async def edit_image(ctx: custom.Context, edit_function: Callable[..., Any], image: objects.Image, **kwargs) -> None:

    embed = utils.embed(
        colour=colours.GREEN,
        emoji=emojis.LOADING,
        description="Processing image"
    )
    message = await ctx.reply(embed=embed)

    image_bytes = await request_image_bytes(session=ctx.bot.session, url=image.url)
    receiving_pipe, sending_pipe = multiprocessing.Pipe(duplex=False)

    process = multiprocessing.Process(target=do_edit_image, daemon=True, args=(edit_function, image_bytes, sending_pipe), kwargs=kwargs)
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, receiving_pipe.recv)

    process.join()

    receiving_pipe.close()
    sending_pipe.close()
    process.terminate()
    process.close()

    if data is ValueError or data is EOFError:

        try:
            await message.delete()
        except Exception:
            pass

        raise exceptions.EmbedError(
            colour=colours.RED,
            description="Something went wrong while editing that image."
        )

    url = await utils.upload_file(ctx.bot.session, file_bytes=data[0], file_format=data[1])

    try:
        await message.delete()
    except Exception:
        pass

    await ctx.reply(url)

    del data


def do_edit_image(edit_function: Callable[..., Any], image_bytes: bytes, pipe: Connection, **kwargs) -> None:

    try:
        with Image(blob=image_bytes) as image, Color("transparent") as colour:

            if image.format != "GIF":
                image.background_color = colour
                edit_function(image, **kwargs)

            else:
                image.coalesce()
                image.iterator_reset()

                image.background_color = colour
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
