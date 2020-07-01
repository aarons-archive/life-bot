"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import io
import multiprocessing
import typing

import discord
from discord.ext import commands
from wand.color import Color
from wand.image import Image
from wand.sequence import SingleImage

from cogs.utilities import exceptions


def blur(image: typing.Union[Image, SingleImage], amount: float):

    image.blur(sigma=amount)
    return image, f'Amount: {amount}'


def edge(image: typing.Union[Image, SingleImage], level: float):

    image.transform_colorspace('gray')
    image.edge(radius=level)
    return image, f'Level: {level}'


def emboss(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.transform_colorspace('gray')
    image.emboss(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def kuwahara(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.kuwahara(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def sharpen(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.adaptive_sharpen(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def spread(image: typing.Union[Image, SingleImage], radius: float):

    image.spread(radius=radius)
    return image, f'Radius: {radius}'


def noise(image: typing.Union[Image, SingleImage], method: str, attenuate: float):

    image.noise(method, attenuate=attenuate)
    return image, f'Method: {method} | Attenuate: {attenuate}'


def blueshift(image: typing.Union[Image, SingleImage], factor: float):

    image.blue_shift(factor=factor)
    return image, f'Factor: {factor}'


def charcoal(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.charcoal(radius=radius, sigma=sigma)
    return image, f'Radius: {radius} | Sigma: {sigma}'


def colorize(image: typing.Union[Image, SingleImage], color: str):

    with Color(color) as image_color:
        with Color('rgb(50%, 50%, 50%)') as image_alpha:
            image.colorize(color=image_color, alpha=image_alpha)

    return image, f'Color: {color}'


def implode(image: typing.Union[Image, SingleImage], amount: float):

    image.implode(amount=amount)
    return image, f'Amount: {amount}'


def polaroid(image: typing.Union[Image, SingleImage], angle: float, caption: str):

    image.polaroid(angle=angle, caption=caption)
    return image, f'Angle: {angle} | Caption: {caption}'


def sepiatone(image: typing.Union[Image, SingleImage], threshold: float):

    image.sepia_tone(threshold=threshold)
    return image, f'Threshold: {threshold}'


def solarize(image: typing.Union[Image, SingleImage], threshold: float):

    image.solarize(threshold=threshold * image.quantum_range)
    return image, f'Threshold: {threshold}'


def swirl(image: typing.Union[Image, SingleImage], degree: float):

    image.swirl(degree=degree)
    return image, f'Degree: {degree}'


def wave(image: typing.Union[Image, SingleImage]):

    image.wave(amplitude=image.height / 32, wave_length=image.width / 4)
    return image, f''


def flip(image: typing.Union[Image, SingleImage]):

    image.flip()
    return image, ''


def flop(image: typing.Union[Image, SingleImage]):

    image.flop()
    return image, ''


def rotate(image: typing.Union[Image, SingleImage], degree: float):

    image.rotate(degree=degree)
    return image, f'Degree: {degree}'


def floor(image: typing.Union[Image, SingleImage]):

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


def do_edit_image(edit_function: typing.Any, image_bytes: bytes, queue: multiprocessing.Queue, **kwargs):

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
                image_format = new_image.format
                new_image.save(file=image_edited)
            else:
                new_image, image_text = edit_function(old_image, **kwargs)
                image_format = new_image.format
                new_image.save(file=image_edited)

    image_edited.seek(0)
    queue.put((image_edited, image_format, image_text))
    return


class Imaging:

    def __init__(self, bot):
        self.bot = bot

        self.queue = multiprocessing.Queue()

    async def get_image_url(self, ctx: commands.Context, argument: str):

        if not argument:
            argument = ctx.author.id

        try:
            member = await commands.MemberConverter().convert(ctx, str(argument))
            argument = str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png'))
        except commands.BadArgument:
            pass

        check_if_url = self.bot.image_url_regex.match(argument)
        if check_if_url is None:
            raise exceptions.ArgumentError('You provided an invalid argument. Please provide a members name, id or '
                                           'mention or an image url.')

        return argument

    async def get_image_bytes(self, url: str):

        async with self.bot.session.get(url) as response:
            image_bytes = await response.read()

        return image_bytes

    async def edit_image(self, ctx: commands.Context, image: str, edit_type: str, **kwargs):

        if edit_type not in image_operations.keys():
            raise exceptions.ArgumentError(f"'{edit_type}' is not a valid image operation")

        image_url = await self.get_image_url(ctx=ctx, argument=image)
        image_bytes = await self.get_image_bytes(url=image_url)

        multiprocessing.Process(target=do_edit_image, kwargs=kwargs, daemon=True,
                                args=(image_operations[edit_type], image_bytes, self.queue)).start()

        image_edited, image_format, image_text = await self.bot.loop.run_in_executor(None, self.queue.get)

        file = discord.File(filename=f'{edit_type}_image.{image_format.lower()}', fp=image_edited)
        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_footer(text=image_text)
        embed.set_image(url=f'attachment://{edit_type}_image.{image_format.lower()}')

        return file, embed
