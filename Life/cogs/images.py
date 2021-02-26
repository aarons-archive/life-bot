#  Life
#  Copyright (C) 10 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

import random
from typing import Literal, Optional

from discord.ext import commands

from bot import Life
from utilities import context, converters, exceptions, imaging


class Images(commands.Cog):
    
    def __init__(self, bot: Life):
        self.bot = bot

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='edge')
    async def edge(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 3, sigma: float = 1.5) -> None:
        """
        Outlines edges within an image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be lower than radius.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='edge', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='blur')
    async def blur(self, ctx: context.Context, image: Optional[converters.ImageConverter], amount: float = 2.0) -> None:
        """
        Blurs the given image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `amount`: The amount to blur the image by.
        """

        if amount < 0.0 or amount > 50.0:
            raise exceptions.ArgumentError('Amount must be between `0.0` and `50.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='blur', amount=amount)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='emboss')
    async def emboss(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 3, sigma: float = 1) -> None:
        """
        Converts the image to greyscale and creates a 3d effect.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be lower than radius.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='emboss', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='kuwahara')
    async def kuwahara(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 2, sigma: float = 1.5) -> None:
        """
        Smooths the given image while preserving edges.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: Filter aperture size.
        `sigma`: Filter standard deviation. Should be `0.5` lower than radius.
        """

        if radius < 0 or radius > 20:
            raise exceptions.ArgumentError('Radius must be between `0` and `20`.')

        if sigma < 0 or sigma > 20:
            raise exceptions.ArgumentError('Sigma must be between `0` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='kuwahara', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='sharpen')
    async def sharpen(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 8, sigma: float = 4) -> None:
        """
        Sharpens the given image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be smaller than radius.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')

        if sigma < 0 or sigma > 50:
            raise exceptions.ArgumentError('Sigma must be between `0` and `50`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='sharpen', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='spread')
    async def spread(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 2.0) -> None:
        """
        Replaces each pixel with one from the surrounding area.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: The area in which to search around a pixel to replace it with.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='spread', radius=radius)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='noise')
    async def noise(self, ctx: context.Context, image: Optional[converters.ImageConverter], attenuate: float = 0.5,
                    method: Literal['uniform', 'gaussian', 'multiplicative_gaussian', 'impulse', 'laplacian', 'poisson', 'random'] = 'uniform') -> None:
        """
        Adds random noise to the given image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `method`: The method to generate noise with.
        `attenuate`: The rate of noise distribution.

        Methods: `uniform`, `gaussian`, `multiplicative_gaussian`, `impulse`, `laplacian`, `poisson`, `random`
        """

        if attenuate < 0 or attenuate > 1:
            raise exceptions.ArgumentError('Attenuate must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='noise', method=method, attenuate=attenuate)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='blueshift')
    async def blueshift(self, ctx: context.Context, image: Optional[converters.ImageConverter], factor: float = 1.25) -> None:
        """
        Creates a moonlight effect by shifting blue colours.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `factor`: The factor to blue-shift colours by.
        """

        if factor < 0 or factor > 20:
            raise exceptions.ArgumentError('Factor must be be between `0` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='blueshift', factor=factor)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='charcoal')
    async def charcoal(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 1.5, sigma: float = 0.5) -> None:
        """
        Redraw the image as if it were drawn with charcoal.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be smaller than radius.
        """

        if radius < -10 or radius > 10:
            raise exceptions.ArgumentError('Radius must be between `-10.0` and `10.0`.')

        if sigma < -5 or sigma > 5:
            raise exceptions.ArgumentError('Sigma must be between `-5.0` and `5.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='charcoal', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='colorize')
    async def colorize(self, ctx: context.Context, image: Optional[converters.ImageConverter], colour: commands.ColourConverter = None) -> None:
        """
        Colorizes the given image with a random colour.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `colour`: The colour code to use. Must be in the format `0xFFFFFF`, `#FFFFFF` or `0x#FFFFFF`.
        """

        if not colour:
            colour = '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='colorize', colour=str(colour))
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='implode')
    async def implode(self, ctx: context.Context, image: Optional[converters.ImageConverter], amount: float = 0.4) -> None:
        """
        Pulls or pushes pixels from the center the image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `amount`: The factor to push or pull pixels by, negative values will push, positives will pull. Best results are -1.0 to 1.0.
        """

        if amount < -20 or amount > 20:
            raise exceptions.ArgumentError('Amount must be between `-20` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='implode', amount=amount)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='polaroid')
    async def polaroid(self, ctx: context.Context, image: Optional[converters.ImageConverter], angle: float = 0.0, *, caption: str = None) -> None:
        """
        Puts the image in the center of a polaroid-like card.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `angle`: The angle that the polaroid will be rotated at.
        `caption`: A caption that will appear on the polaroid.
        """

        if angle < -360 or angle > 360:
            raise exceptions.ArgumentError('Angle must be between `-360` and `360`.')

        if caption and len(caption) > 100:
            raise exceptions.ArgumentError('Caption must be `100` characters or less.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='polaroid', angle=angle, caption=caption)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='sepiatone')
    async def sepia_tone(self, ctx: context.Context, image: Optional[converters.ImageConverter], threshold: float = 0.8) -> None:
        """
        Applies a filter that simulates chemical photography.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `threshold`: The factor to tone the image by.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='sepiatone', threshold=threshold)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='solarize')
    async def solarize(self, ctx: context.Context, image: Optional[converters.ImageConverter], threshold: float = 0.5) -> None:
        """
        Replaces pixels above the threshold with negated ones.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `threshold`: Threshold to select pixels with.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='solarize', threshold=threshold)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='swirl')
    async def swirl(self, ctx: context.Context, image: Optional[converters.ImageConverter], degree: int = 45) -> None:
        """
        Swirls pixels around the center of the image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `degree`: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='swirl', degree=degree)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='wave')
    async def wave(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a wave like effect on the image.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='wave')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='flip')
    async def flip(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Flips the image along the x-axis.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='flip')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='flop')
    async def flop(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Flips the image along the y-axis.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='flop')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='rotate')
    async def rotate(self, ctx: context.Context, image: Optional[converters.ImageConverter], degree: int = 45) -> None:
        """
        Rotates the image an amount of degrees.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        `degree`: The amount of degrees to rotate the image.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='rotate', degree=degree)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='floor')
    async def floor(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Warps and tiles the image which makes it like a floor.

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='floor')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='cube')
    async def cube(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a cube!

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='cube')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='bounce')
    async def bounce(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Make the image bounce?

        `image`: Can be a members name, id or @mention, an image url or an attachment.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='bounce')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='colours', aliases=['colors'])
    async def colours(self, ctx: context.Context, image: Optional[converters.ImageConverter], *, colours: int = 10) -> None:

        if colours > 1024:
            raise exceptions.ArgumentError('Number of colours must be less than 1024.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='colours', number_colours=colours)
            await ctx.reply(embed=embed)



def setup(bot: Life):
    bot.add_cog(Images(bot))
