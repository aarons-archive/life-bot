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
from typing import Any, Union

import aiohttp
import discord
from wand.color import Color
from wand.exceptions import MissingDelegateError
from wand.image import Image
from wand.sequence import SingleImage

import config
from utilities import context
from utilities.exceptions import ArgumentError, ImageError


def edge(image: Union[Image, SingleImage], radius: float, sigma: float):

    image.canny(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def blur(image: Union[Image, SingleImage], amount: float):

    image.blur(sigma=amount)
    return image, f'Amount: {amount}'


def emboss(image: Union[Image, SingleImage], radius: float, sigma: float):

    image.transform_colorspace('gray')
    image.emboss(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def kuwahara(image: Union[Image, SingleImage], radius: float, sigma: float):

    image.kuwahara(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def sharpen(image: Union[Image, SingleImage], radius: float, sigma: float):

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def spread(image: Union[Image, SingleImage], radius: float):

    image.spread(radius=radius)
    return image, f'Radius: {radius}'


def noise(image: Union[Image, SingleImage], method: str, attenuate: float):

    image.noise(method, attenuate=attenuate)
    return image, f'Method: {method} | Attenuate: {attenuate}'


def blueshift(image: Union[Image, SingleImage], factor: float):

    image.blue_shift(factor=factor)
    return image, f'Factor: {factor}'


def charcoal(image: Union[Image, SingleImage], radius: float, sigma: float):

    image.charcoal(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def colorize(image: Union[Image, SingleImage], colour: str):

    with Color(colour) as image_colour:
        with Color('rgb(50%, 50%, 50%)') as image_alpha:
            image.colorize(color=image_colour, alpha=image_alpha)

    return image, f'Color: {colour}'


def implode(image: Union[Image, SingleImage], amount: float):

    image.implode(amount=amount)
    return image, f'Amount: {amount}'


def polaroid(image: Union[Image, SingleImage], angle: float, caption: str):

    image.polaroid(angle=angle, caption=caption)
    return image, f'Angle: {angle} | Caption: {caption}'


def sepiatone(image: Union[Image, SingleImage], threshold: float):

    image.sepia_tone(threshold=threshold)
    return image, f'Threshold: {threshold}'


def solarize(image: Union[Image, SingleImage], threshold: float):

    image.solarize(threshold=threshold * image.quantum_range)
    return image, f'Threshold: {threshold}'


def swirl(image: Union[Image, SingleImage], degree: float):

    image.swirl(degree=degree)
    return image, f'Degree: {degree}'


def wave(image: Union[Image, SingleImage]):

    image.wave(amplitude=image.height / 32, wave_length=image.width / 4)
    return image, ''


def flip(image: Union[Image, SingleImage]):

    image.flip()
    return image, ''


def flop(image: Union[Image, SingleImage]):

    image.flop()
    return image, ''


def rotate(image: Union[Image, SingleImage], degree: float):

    image.rotate(degree=degree)
    return image, f'Degree: {degree}'


def floor(image: Union[Image, SingleImage]):

    image.virtual_pixel = 'tile'
    arguments = (0,            0,            image.width * 0.2, image.height * 0.5,
                 image.width,  0,            image.width * 0.8, image.height * 0.5,
                 0,            image.height, image.width * 0.1, image.height,
                 image.width,  image.height, image.width * 0.9, image.height)
    image.distort('perspective', arguments)

    return image, ''


image_operations = {
    'blur': blur,
    'edge': edge,
    'emboss': emboss,
    'kuwahara': kuwahara,
    'sharpen': sharpen,
    'spread': spread,
    'noise': noise,
    'blueshift': blueshift,
    'charcoal': charcoal,
    'colorize': colorize,
    'implode': implode,
    'polaroid': polaroid,
    'sepiatone': sepiatone,
    'solarize': solarize,
    'swirl': swirl,
    'wave': wave,
    'flip': flip,
    'flop': flop,
    'rotate': rotate,
    'floor': floor
}


def do_edit_image(edit_function: Any, image_bytes: bytes, child_pipe: multiprocessing.Pipe, **kwargs):

    try:

        image_original = io.BytesIO(image_bytes)
        image_edited = io.BytesIO()

        with Image(file=image_original) as old_image:
            with Image() as new_image:

                image_format = old_image.format
                if image_format == 'GIF':
                    old_image.coalesce()
                    for old_frame in old_image.sequence:
                        new_frame, image_text = edit_function(old_frame, **kwargs)
                        new_image.sequence.append(new_frame)
                else:
                    new_image, image_text = edit_function(old_image, **kwargs)

                image_format = new_image.format
                new_image.save(file=image_edited)

        image_edited.seek(0)

        child_pipe.send({
            'image': image_edited,
            'format': image_format,
            'text': image_text
        })

        image_original.close()
        image_edited.close()

    except MissingDelegateError:
        child_pipe.send(ImageError())


async def edit_image(ctx: context.Context, edit_type: str,  url: str = None, **kwargs) -> discord.Embed:

    if ctx.message.attachments:
        url = ctx.message.attachments[0].url
    if url is None:
        url = str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() is True else 'png'))

    async with ctx.bot.session.get(url) as response:

        if response.status != 200:
            raise ArgumentError('Something went wrong while loading that image, check the url or try again later.')

        if response.headers.get('Content-Type') not in ['image/png', 'image/gif', 'image/jpeg', 'image/webp']:
            raise ImageError('That file format is not allowed, only png, gif, jpg and webp are allowed.')

        if (content_length := response.headers.get('Content-Length')) and int(content_length) > 20971520:
            raise ImageError('The image provided was too big for me to edit, please keep to a `20mb` maximum')

        image_bytes = await response.read()

    parent_pipe, child_pipe = multiprocessing.Pipe()
    process = multiprocessing.Process(target=do_edit_image, kwargs=kwargs, daemon=True, args=(image_operations[edit_type], image_bytes, child_pipe))
    process.start()

    data = await ctx.bot.loop.run_in_executor(None, parent_pipe.recv)
    if isinstance(data, ImageError):
        process.terminate()
        raise ImageError('Something went wrong while trying to edit that image.')

    process.join()
    process.close()

    form_data = aiohttp.FormData()
    form_data.add_field('file', data['image'], filename=f'image.{data["format"].lower()}')

    async with ctx.bot.session.post('https://media.mrrandom.xyz/api/media', headers={"Authorization": config.AXEL_WEB_TOKEN}, data=form_data) as response:

        if response.status == 413:
            raise ImageError('The image produced was too large to upload.')

        post = await response.json()

    embed = discord.Embed(colour=ctx.colour)
    embed.set_footer(text=data['text'])
    embed.set_image(url=f'https://media.mrrandom.xyz/{post.get("filename")}')
    return embed
