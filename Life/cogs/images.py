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
    @commands.command(name='adaptive_blur', aliases=['ab'])
    async def adaptive_blur(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 8, sigma: float = 4) -> None:
        """
        Blurs the image only where edges are not detected.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='adaptive_blur', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='adaptive_sharpen', aliases=['as'])
    async def adaptive_sharpen(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 8, sigma: float = 4) -> None:
        """
        Sharpens the image only where edges are detected.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')
        if sigma < 0 or sigma > 50:
            raise exceptions.ArgumentError('Sigma must be between `0` and `50`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='adaptive_sharpen', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='blue_shift', aliases=['blueshift', 'bs'])
    async def blueshift(self, ctx: context.Context, image: Optional[converters.ImageConverter], factor: float = 1.25) -> None:
        """
        Creates a "nighttime moonlight" effect by shifting blue colours.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `factor`: The factor to shift blue colours by.
        """

        if factor < 0 or factor > 20:
            raise exceptions.ArgumentError('Factor must be be between `0` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='blueshift', factor=factor)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='blur')
    async def blur(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 0, sigma: float = 3) -> None:
        """
        Blurs the given image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='blur', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='border')
    async def border(self, ctx: context.Context, image: Optional[converters.ImageConverter], colour: commands.ColourConverter = None, width: int = 10, height: int = 10) -> None:
        """
        Creates a border around the given image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `colour`: The colour of the border. Possible formats include `0x<hex>`, `#<hex>`, `0x#<hex>` and `rgb(<number>, <number>, <number>)`. `<number>` can be `0 - 255` or `0% to 100%` and `<hex>` can be `#FFF` or `#FFFFFF`.
        `width`: The width of the border.
        `height`: The height of the border.
        """

        if not colour:
            colour = '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='border', colour=str(colour), width=width, height=height)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='edge')
    async def edge(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 0, sigma: float = 1) -> None:
        """
        Outlines edges within an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='edge', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='charcoal')
    async def charcoal(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 1.5, sigma: float = 0.5) -> None:
        """
        Redraw the image as if it were drawn with charcoal.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < -10 or radius > 10:
            raise exceptions.ArgumentError('Radius must be between `-10.0` and `10.0`.')
        if sigma < -5 or sigma > 5:
            raise exceptions.ArgumentError('Sigma must be between `-5.0` and `5.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='charcoal', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='colorize', aliases=['colourise'])
    async def colorize(self, ctx: context.Context, image: Optional[converters.ImageConverter], colour: commands.ColourConverter = None) -> None:
        """
        Colorizes the given image with a random colour.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `colour`: The colour of the border. Possible formats include `0x<hex>`, `#<hex>`, `0x#<hex>` and `rgb(<number>, <number>, <number>)`. `<number>` can be `0 - 255` or `0% to 100%` and `<hex>` can be `#FFF` or `#FFFFFF`.
        """

        if not colour:
            colour = '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='colorize', colour=str(colour))
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='despeckle')
    async def despeckle(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Removes noise from an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='despeckle')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='floor')
    async def floor(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Warps and tiles the image which makes it like a floor.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='floor')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='emboss')
    async def emboss(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 3, sigma: float = 1) -> None:
        """
        Creates a 3D effect within the image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='emboss', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='enhance')
    async def enhance(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Removes noise from an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='enhance')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='flip')
    async def flip(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Flips the image along the x-axis.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='flip')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='flop')
    async def flop(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Flips the image along the y-axis.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='flop')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='frame')
    async def frame(self, ctx: context.Context, image: Optional[converters.ImageConverter], colour: commands.ColourConverter = None, width: int = 20, height: int = 20,
                    inner: int = 5, outer: int = 10) -> None:
        """
        Creates a frame around the given image with a 3D effect.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        `colour`: The colour of the frame. Possible formats include `0x<hex>`, `#<hex>`, `0x#<hex>` and `rgb(<number>, <number>, <number>)`. `<number>` can be `0 - 255` or `0% to 100%` and `<hex>` can be `#FFF` or `#FFFFFF`.
        `width`: The width of the frame.
        `height`: The height of the frame.
        `inner`: The inner bevel of the frame.
        `outer`: The outer bevel of the frame.
        """

        if not colour:
            colour = '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='frame', matte=str(colour), height=height, width=width, inner_bevel=inner, outer_bevel=outer)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='gaussian_blur', aliases=['gb'])
    async def gaussian_blur(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 0, sigma: float = 3) -> None:
        """
        Blurs the given image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='gaussian_blur', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='implode', aliases=['explode'])
    async def implode(self, ctx: context.Context, image: Optional[converters.ImageConverter], amount: float = 0.4) -> None:
        """
        Pulls or pushes pixels from the center the image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `amount`: The factor to push or pull pixels by, negative values will push, positives will pull. Best results are -1.0 to 1.0.
        """

        if amount < -20 or amount > 20:
            raise exceptions.ArgumentError('Amount must be between `-20` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='implode', amount=amount)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='colours', aliases=['colors'])
    async def colours(self, ctx: context.Context, image: Optional[converters.ImageConverter], *, colours: int = 10) -> None:
        """
        Reduces the amount of colours in an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `colours`: The amount of colours to keep in the image.
        """

        if colours > 1024:
            raise exceptions.ArgumentError('Number of colours must be less than 1024.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='kmeans', number_colours=colours)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='kuwahara')
    async def kuwahara(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 3, sigma: float = 2.5) -> None:
        """
        Smooths the given image while preserving edges.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 20:
            raise exceptions.ArgumentError('Radius must be between `0` and `20`.')
        if sigma < 0 or sigma > 20:
            raise exceptions.ArgumentError('Sigma must be between `0` and `20`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='kuwahara', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='motion_blur', aliases=['mb'])
    async def motion_blur(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 20, sigma: float = 10, angle: int = 45) -> None:
        """
        Apply a blur along an angle.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        `angle`: The angle at which to apply the blur.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='motion_blur', radius=radius, sigma=sigma, angle=angle)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='negate')
    async def negate(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Negates the colours in an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='negate')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='noise')
    async def noise(self, ctx: context.Context, image: Optional[converters.ImageConverter], attenuate: float = 0.5,
                    method: Literal['uniform', 'gaussian', 'multiplicative_gaussian', 'impulse', 'laplacian', 'poisson', 'random'] = 'impulse') -> None:
        """
        Adds random noise to an image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `attenuate`: The rate of noise distribution.
        `method`: The method to generate noise with.

        Methods: `uniform`, `gaussian`, `multiplicative_gaussian`, `impulse`, `laplacian`, `poisson`, `random`.
        """

        if attenuate < 0 or attenuate > 1:
            raise exceptions.ArgumentError('Attenuate must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='noise', method=method, attenuate=attenuate)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='oil_paint', aliases=['op'])
    async def oil_paint(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 2, sigma: float = 1) -> None:
        """
        Edits the image to look like an oil painting.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='oil_paint', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='polaroid')
    async def polaroid(self, ctx: context.Context, image: Optional[converters.ImageConverter], angle: float = 0, *, caption: str = None) -> None:
        """
        Puts the image in the center of a polaroid-like card.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
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
    @commands.command(name='rotate')
    async def rotate(self, ctx: context.Context, image: Optional[converters.ImageConverter], degree: int = 45) -> None:
        """
        Rotates the image an amount of degrees.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `degree`: The amount of degrees to rotate the image.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='rotate', degree=degree)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='sepia_tone', aliases=['st'])
    async def sepia_tone(self, ctx: context.Context, image: Optional[converters.ImageConverter], threshold: float = 0.8) -> None:
        """
        Applies a filter that simulates chemical photography.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `threshold`: The factor to tone the image by.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='sepia_tone', threshold=threshold)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='sharpen')
    async def sharpen(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 8, sigma: float = 4) -> None:
        """
        Sharpens the given image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.

        If you don't know what these do, its probably best to leave them alone:
        `radius`: Size of gaussian aperture. Should be larger than `sigma`.
        `sigma`: Standard deviation of the gaussian filter.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')
        if sigma < 0 or sigma > 50:
            raise exceptions.ArgumentError('Sigma must be between `0` and `50`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='sharpen', radius=radius, sigma=sigma)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='solarize')
    async def solarize(self, ctx: context.Context, image: Optional[converters.ImageConverter], threshold: float = 0.5) -> None:
        """
        Replaces pixels above the threshold with negated ones.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `threshold`: Threshold to select pixels with.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='solarize', threshold=threshold)
            await ctx.reply(embed=embed)


    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='spread')
    async def spread(self, ctx: context.Context, image: Optional[converters.ImageConverter], radius: float = 2.0) -> None:
        """
        Replaces each pixel with one from the surrounding area.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `radius`: The area in which to search around a pixel to replace it with.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='spread', radius=radius)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='swirl')
    async def swirl(self, ctx: context.Context, image: Optional[converters.ImageConverter], degree: int = 45) -> None:
        """
        Swirls pixels around the center of the image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `degree`: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='swirl', degree=degree)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='transparentize')
    async def transparentize(self, ctx: context.Context, image: Optional[converters.ImageConverter], transparency: float = 0.5) -> None:
        """
        Makes an image transparent.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        `degree`: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        if transparency < 0.0 or transparency > 1.0:
            raise exceptions.ArgumentError('Transparency must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='transparentize', transparency=transparency)
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='transpose')
    async def transpose(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a vertical mirror image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='transpose')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='transverse')
    async def transverse(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a horizontal mirror image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='transverse')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='wave')
    async def wave(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a wave like effect on the image.

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='wave')
            await ctx.reply(embed=embed)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name='cube')
    async def cube(self, ctx: context.Context, image: Optional[converters.ImageConverter]) -> None:
        """
        Creates a cube!

        `image`: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or an image url.
        """

        async with ctx.channel.typing():
            embed = await imaging.edit_image(ctx=ctx, url=image, edit_type='cube')
            await ctx.reply(embed=embed)


def setup(bot: Life):
    bot.add_cog(Images(bot))
