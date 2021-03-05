#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#


import io
import multiprocessing
import sys
from typing import Callable, Optional, Union

import aiohttp
import bs4
import discord
import humanize
import yarl
from wand.color import Color
from wand.image import Image
from wand.sequence import SingleImage

import config
from utilities import context, exceptions


def adaptive_blur(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.adaptive_blur(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def adaptive_sharpen(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def blueshift(image: Union[Image, SingleImage], factor: float = 1.5) -> Optional[str]:

    image.blue_shift(factor=factor)
    return f'Factor: {factor}'


def blur(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.blur(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def border(image: Union[Image, SingleImage], colour: str, width: int = 1, height: int = 1) -> Optional[str]:

    with Color(colour) as color:
        image.border(color=color, width=width, height=height, compose='atop')
    return f'Colour: {colour} | Width: {width} | Height: {height}'


def edge(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 1) -> Optional[str]:

    image.canny(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def charcoal(image: Union[Image, SingleImage], radius: float, sigma: float) -> Optional[str]:

    image.charcoal(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def colorize(image: Union[Image, SingleImage], colour: str = None) -> Optional[str]:

    with Color(colour) as colour:
        with Color('rgb(50%, 50%, 50%)') as alpha:
            image.colorize(color=colour, alpha=alpha)

    return f'Colour: {colour}'


def despeckle(image: Union[Image, SingleImage]) -> Optional[str]:

    image.despeckle()
    return


def floor(image: Union[Image, SingleImage]) -> Optional[str]:

    image.virtual_pixel = 'tile'
    arguments = (0,            0,            image.width * 0.2, image.height * 0.5,
                 image.width,  0,            image.width * 0.8, image.height * 0.5,
                 0,            image.height, image.width * 0.1, image.height,
                 image.width,  image.height, image.width * 0.9, image.height)
    image.distort('perspective', arguments)

    return


def emboss(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.transform_colorspace('gray')
    image.emboss(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def enhance(image: Union[Image, SingleImage]) -> Optional[str]:

    image.enhance()
    return


def flip(image: Union[Image, SingleImage]) -> Optional[str]:

    image.flip()
    return None


def flop(image: Union[Image, SingleImage]) -> Optional[str]:

    image.flop()
    return None


def frame(image: Union[Image, SingleImage], matte: str, width: int = 10, height: int = 10, inner_bevel: float = 5, outer_bevel: float = 5) -> Optional[str]:

    with Color(matte) as color:
        image.frame(matte=color, width=width, height=height, inner_bevel=inner_bevel, outer_bevel=outer_bevel)

    return f'Colour: {matte} | Width: {width} | Height: {height} | Inner bevel: {inner_bevel} | Outer bevel: {outer_bevel}'


def gaussian_blur(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.gaussian_blur(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def implode(image: Union[Image, SingleImage], amount: float) -> Optional[str]:

    image.implode(amount=amount)
    return f'Amount: {amount}'


def kmeans(image: Union[Image, SingleImage], number_colours: int = None) -> Optional[str]:

    image.kmeans(number_colors=number_colours)
    return f'Number of colours: {number_colours}'


def kuwahara(image: Union[Image, SingleImage], radius: float = 1, sigma: float = None) -> Optional[str]:

    image.kuwahara(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def motion_blur(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0, angle: float = 0) -> Optional[str]:

    image.motion_blur(radius=radius, sigma=sigma, angle=angle)
    return f'Radius: {radius} | Sigma: {sigma} | Angle: {angle}'


def negate(image: Union[Image, SingleImage]) -> Optional[str]:

    image.negate(channel='rgb')
    return


def noise(image: Union[Image, SingleImage], method: str = 'uniform', attenuate: float = 1) -> Optional[str]:

    image.noise(method, attenuate=attenuate)
    return f'Method: {method} | Attenuate: {attenuate}'


def oil_paint(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.oil_paint(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def polaroid(image: Union[Image, SingleImage], angle: float = 0, caption: str = None) -> Optional[str]:

    image.polaroid(angle=angle, caption=caption)
    return f'Angle: {angle} | Caption: {caption}'


def rotate(image: Union[Image, SingleImage], degree: float, reset: bool = True) -> Optional[str]:

    image.rotate(degree=degree, reset_coords=reset)
    return f'Degree: {degree} | Reset: {reset}'


def sepia_tone(image: Union[Image, SingleImage], threshold: float = 0.8) -> Optional[str]:

    image.sepia_tone(threshold=threshold)
    return f'Threshold: {threshold}'


def sharpen(image: Union[Image, SingleImage], radius: float = 0, sigma: float = 0) -> Optional[str]:

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return f'Radius: {radius} | Sigma: {sigma}'


def solarize(image: Union[Image, SingleImage], threshold: float = 0.5) -> Optional[str]:

    image.solarize(threshold=threshold, channel='rgb')
    return f'Threshold: {threshold}'


def spread(image: Union[Image, SingleImage], radius: float) -> Optional[str]:

    image.spread(radius=radius)
    return f'Radius: {radius}'


def swirl(image: Union[Image, SingleImage], degree: float) -> Optional[str]:

    image.swirl(degree=degree)
    return f'Degree: {degree}'


def transparentize(image: Union[Image, SingleImage], transparency: float) -> Optional[str]:

    image.transparentize(transparency=transparency)
    return f'Transparency: {transparency}'


def transpose(image: Union[Image, SingleImage]) -> Optional[str]:

    image.transpose()
    return


def transverse(image: Union[Image, SingleImage]) -> Optional[str]:

    image.transverse()
    return


def wave(image: Union[Image, SingleImage]) -> Optional[str]:

    image.wave(amplitude=image.height / 32, wave_length=image.width / 4)
    return


def cube(image: Union[Image, SingleImage]) -> Optional[str]:

    def d3(x: int):
        return int(x / 3)

    image.resize(1000, 1000)
    image.alpha_channel = 'opaque'

    top = Image(image)
    top.resize(d3(1000), d3(860))
    top.shear(x=-30, background=Color('none'))
    top.rotate(degree=-30)

    right = Image(image)
    right.resize(d3(1000), d3(860))
    right.shear(background=Color('none'), x=30)
    right.rotate(degree=-30)

    left = Image(image)
    left.resize(d3(1000), d3(860))
    left.shear(background=Color('none'), x=-30)
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
    return ''




IMAGE_OPERATIONS = {
    'adaptive_blur': adaptive_blur,
    'adaptive_sharpen': adaptive_sharpen,
    'blueshift': blueshift,
    'blur': blur,
    'border': border,
    'edge': edge,
    'charcoal': charcoal,
    'colorize': colorize,
    'despeckle': despeckle,
    'floor': floor,
    'emboss': emboss,
    'enhance': enhance,
    'flip': flip,
    'flop': flop,
    'frame': frame,
    'gaussian_blur': gaussian_blur,
    'implode': implode,
    'kmeans': kmeans,
    'kuwahara': kuwahara,
    'motion_blur': motion_blur,
    'negate': negate,
    'noise': noise,
    'oil_paint': oil_paint,
    'polaroid': polaroid,
    'rotate': rotate,
    'sepia_tone': sepia_tone,
    'sharpen': sharpen,
    'solarize': solarize,
    'spread': spread,
    'swirl': swirl,
    'transparentize': transparentize,
    'transpose': transpose,
    'transverse': transverse,
    'wave': wave,
    'cube': cube,
}

MAX_CONTENT_SIZE = (2 ** 20) * 25
VALID_CONTENT_TYPES = ['image/gif', 'image/heic', 'image/jpeg', 'image/png', 'image/webp', 'image/avif', 'image/svg+xml']
COMMON_GIF_SITES = ['tenor.com', 'giphy.com']

CDN_UPLOAD_URL = 'https://media.mrrandom.xyz/api/media'
CDN_HEADERS = {'Authorization': config.AXEL_WEB_TOKEN}


def _do_edit_image(child_pipe: multiprocessing.Pipe, edit_function: Callable, image_bytes: bytes, **kwargs):

    try:

        image_buffer = io.BytesIO(image_bytes)
        image_edited_buffer = io.BytesIO()

        with Image(file=image_buffer) as image:

            image_format = image.format
            if image_format != 'GIF':
                text = edit_function(image, **kwargs)
            else:
                image.coalesce()
                for x in image.sequence:
                    with x as image_frame:
                        text = edit_function(image_frame, **kwargs)
                image.optimize_transparency()
                image.optimize_layers()

            image.save(file=image_edited_buffer)

        image_edited_buffer.seek(0)

        child_pipe.send({
            'image': image_edited_buffer,
            'image_format': image_format,
            'text': text
        })

        image_buffer.close()
        image_edited_buffer.close()

    except Exception as e:
        print(e, file=sys.stderr)
        child_pipe.send(exceptions.ImageError())


async def _request_image_bytes(*, ctx: context.Context, url: str) -> bytes:

    async with ctx.bot.session.get(url) as request:

        if yarl.URL(url).host in COMMON_GIF_SITES:
            page = bs4.BeautifulSoup(await request.text(), features='html.parser')
            if (url := page.find("meta",  property="og:url")) is not None:
                return await _request_image_bytes(ctx=ctx, url=url['content'])

        if request.status != 200:
            raise exceptions.ImageError('Something went wrong while loading that image, check the url or try again later.')
        elif request.headers.get('Content-Type') not in VALID_CONTENT_TYPES:
            raise exceptions.ImageError('That image format is not allowed. Valid formats include `gif`, `heic`, `jpeg`, `png`, `webp`, `avif` and `svg`.')
        elif (content_length := request.headers.get('Content-Length', 0)) and int(content_length) > MAX_CONTENT_SIZE:
            raise exceptions.ImageError(f'That image was too big to edit, please keep to a `{humanize.naturalsize(MAX_CONTENT_SIZE)}` maximum')

        return await request.read()


async def _upload_image(*, ctx: context.Context, image: io.BytesIO, image_format: str, text: str = None) -> discord.Embed:

    data = aiohttp.FormData()
    data.add_field('file', image, filename=f'image.{image_format.lower()}')

    async with ctx.bot.session.post(CDN_UPLOAD_URL, headers=CDN_HEADERS, data=data) as response:

        if response.status == 413:
            raise exceptions.ImageError('The image produced was too large to upload.')

        post = await response.json()

    embed = discord.Embed(colour=ctx.colour)
    embed.set_image(url=f'https://media.mrrandom.xyz/{post.get("filename")}')
    if text:
        embed.set_footer(text=text)

    return embed


#


async def edit_image(*, ctx: context.Context, edit_type: str,  url: str = None, **kwargs) -> discord.Embed:

    if ctx.message.attachments:
        url = ctx.message.attachments[0].url
    if url is None:
        url = str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() is True else 'png'))

    image_bytes = await _request_image_bytes(ctx=ctx, url=url)
    parent_pipe, child_pipe = multiprocessing.Pipe()

    process = multiprocessing.Process(target=_do_edit_image, daemon=True, args=(child_pipe, IMAGE_OPERATIONS[edit_type], image_bytes), kwargs=kwargs)
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, parent_pipe.recv)
    if isinstance(data, (exceptions.ImageError, EOFError)):
        process.terminate()
        raise exceptions.ImageError('Something went wrong while trying to edit that image.')

    process.join()

    process.close()
    parent_pipe.close()
    child_pipe.close()

    embed = await _upload_image(ctx=ctx, image=data['image'], image_format=data['image_format'], text=data['text'])
    return embed
