# Future
from __future__ import annotations

# Standard Library
from inspect import Parameter
from typing import Any, Optional

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours, config, emojis
from core.bot import Life
from utilities import custom, exceptions, imaging, objects, utils


_old_transform = commands.Command.transform


def _new_transform(self, ctx: custom.Context, param: Parameter) -> Any:

    if param.annotation is Optional[objects.Image]:

        message = ctx.message
        if reference := ctx.message.reference:
            message = reference.cached_message or (reference.resolved if isinstance(reference.resolved, discord.Message) else ctx.message)

        default = None

        if attachments := message.attachments:
            default = objects.Image(attachments[0].url)

        elif embeds := message.embeds:
            if (image := embeds[0].image) or (image := embeds[0].thumbnail):
                default = objects.Image(image.url)

        param = Parameter(name=param.name, kind=param.kind, default=default or objects.Image(utils.avatar(ctx.author)), annotation=param.annotation)

    return _old_transform(self=self, ctx=ctx, param=param)


commands.Command.transform = _new_transform


def setup(bot: Life) -> None:
    bot.add_cog(Images(bot))


class Images(commands.Cog):

    def __init__(self, bot: Life, /) -> None:
        self.bot: Life = bot

    @staticmethod
    def limit(person: discord.User | discord.Member, name: str, value: float, minimum: float, maximum: float) -> None:

        if (minimum < value > maximum) and person.id not in config.OWNER_IDS:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{name}** must be between **{minimum}** and **{maximum}**.",
            )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="blur")
    async def blur(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Blurs the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.blur, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="adaptive-blur", aliases=["adaptive_blur", "adaptiveblur", "ab"])
    async def adaptive_blur(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Blurs the image where there are no edges.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.adaptive_blur, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="sharpen")
    async def sharpen(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Sharpens the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.sharpen, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="adaptive-sharpen", aliases=["adaptive_sharpen", "adaptivesharpen", "as"])
    async def adaptive_sharpen(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Sharpens the image where edges are detected.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.adaptive_sharpen, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="blue-shift", aliases=["blue_shift", "blueshift", "bs"])
    async def blueshift(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        factor: float = 1.25
    ) -> None:
        """
        Creates a nighttime moonlight effect by shifting blue colour values.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **factor**: The factor to shift blue colour values by.
        """

        self.limit(person=ctx.author, name="factor", value=factor, minimum=0, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.blueshift, image=image, factor=factor)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="border")
    async def border(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        colour: commands.ColourConverter = utils.MISSING,
        width: int = 20,
        height: int = 20,
    ) -> None:
        """
        Creates a border around the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **colour**: The colour of the border.
        **width**: The width of the border.
        **height**: The height of the border.

        __**Colour formats**__:
        - 0x<hex>
        - #<hex>
        - 0x#<hex>
        - rgb(<number>, <number>, <number>)
        - Any colour from [this](https://discordpy.readthedocs.io/en/master/api.html?highlight=colour#discord.Colour) list.

         **<number>** can be in the range of **0** to **255** or **0%** to **100%**
         **<hex>** can be **#FFF** or **#FFFFFF**.
        """

        await imaging.edit_image(
            ctx=ctx,
            edit_function=imaging.border,
            image=image,
            colour=str(colour) if colour else utils.random_hex(),
            width=width,
            height=height,
        )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="colorize", aliases=["colourize", "colorise", "colourise"])
    async def colorize(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        colour: Optional[commands.ColourConverter]
    ) -> None:
        """
        Colorizes the given image with a random colour.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        **colour**: The colour of the border.

        __**Colour formats**__:
        - 0x<hex>
        - #<hex>
        - 0x#<hex>
        - rgb(<number>, <number>, <number>)
        - Any colour from [this](https://discordpy.readthedocs.io/en/master/api.html?highlight=colour#discord.Colour) list.

         **<number>** can be in the range of **0** to **255** or **0%** to **100%**
         **<hex>** can be **#FFF** or **#FFFFFF**.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.colorize, image=image, colour=str(colour) if colour else utils.random_hex())

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="despeckle")
    async def despeckle(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Removes noise from an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.despeckle, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="floor")
    async def floor(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Warps and tiles the image which makes it like a floor.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.floor, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="emboss")
    async def emboss(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 3,
        sigma: float = 1
    ) -> None:
        """
        Creates a 3D effect within the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.emboss, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="enhance")
    async def enhance(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Removes noise from an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.enhance, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="flip")
    async def flip(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Flips the image along the x-axis.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.flip, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="flop")
    async def flop(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Flips the image along the y-axis.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.flop, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="frame")
    async def frame(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        colour: Optional[commands.ColourConverter],
        width: int = 20,
        height: int = 20,
        inner: int = 5,
        outer: int = 10,
    ) -> None:
        """
        Creates a frame around the given image with a 3D effect.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **colour**: The colour of the frame.
        **width**: The width of the frame.
        **height**: The height of the frame.
        **inner**: The inner bevel of the frame.
        **outer**: The outer bevel of the frame.

        __**Colour formats**__:
        - 0x<hex>
        - #<hex>
        - 0x#<hex>
        - rgb(<number>, <number>, <number>)
        - Any colour from [this](https://discordpy.readthedocs.io/en/master/api.html?highlight=colour#discord.Colour) list.

         **<number>** can be in the range of **0** to **255** or **0%** to **100%**
         **<hex>** can be **#FFF** or **#FFFFFF**.
        """

        await imaging.edit_image(
            ctx=ctx,
            edit_function=imaging.frame,
            image=image,
            matte=str(colour) if colour else utils.random_hex(),
            height=height,
            width=width,
            inner_bevel=inner,
            outer_bevel=outer,
        )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="implode", aliases=["explode"])
    async def implode(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        factor: float = 0.4,
        *,
        method: imaging.PixelInterpolateMethods = "undefined",
    ) -> None:
        """
        Pulls or pushes pixels from the center the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        **factor**: The factor to push or pull pixels by, negative values will push, positives will pull. For the best results use -1.0 to 1.0.
        """

        self.limit(person=ctx.author, name="factor", value=factor, minimum=-20, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.implode, image=image, amount=factor, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="kmeans")
    async def kmeans(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        colors: int = 10
    ) -> None:
        """
        Reduces the amount of colours in an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        **colors**: The amount of colours to keep in the image.
        """

        self.limit(person=ctx.author, name="colours", value=colors, minimum=0, maximum=1024)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.kmeans, image=image, number_colours=colors)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="kuwahara")
    async def kuwahara(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 5,
        sigma: float = 2.5
    ) -> None:
        """
        Smooths the given image while preserving edges.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=20)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.kuwahara, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="motion-blur", aliases=["motion_blur", "motionblur", "mb"])
    async def motion_blur(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 30,
        sigma: float = 20,
        angle: int = 90,
    ) -> None:
        """
        Applies a blur along an angle.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.motion_blur, image=image, radius=radius, sigma=sigma, angle=angle)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="invert", aliases=["negate"])
    async def invert(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image]
    ) -> None:
        """
        Inverts the colours in an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.negate, image=image)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="noise")
    async def noise(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        attenuate: float = 0.5,
        method: imaging.NoiseTypes = "impulse",
    ) -> None:
        """
        Adds random noise to an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **attenuate**: The rate of noise distribution.
        **method**: The method to generate noise with.

        Methods: **undefined**, **uniform**, **gaussian**, **multiplicative_gaussian**, **impulse**, **laplacian**, **poisson**, **random**.
        """

        self.limit(person=ctx.author, name="attenuate", value=attenuate, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.noise, image=image, method=method, attenuate=attenuate)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="oil-paint", aliases=["oil_paint", "oilpaint", "op"])
    async def oil_paint(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 2,
        sigma: float = 1
    ) -> None:
        """
        Edits the image to look like an oil painting.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.oil_paint, image=image, radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="polaroid")
    async def polaroid(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        angle: float = 0,
        *,
        caption: Optional[str]
    ) -> None:
        """
        Puts the image in the center of a polaroid-like card.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **angle**: The angle that the polaroid will be rotated at.
        **caption**: A caption that will appear on the polaroid.
        """

        self.limit(person=ctx.author, name="angle", value=angle, minimum=-360, maximum=360)

        if caption and len(caption) > 100:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="**caption** must be **100** characters or less."
            )

        await imaging.edit_image(ctx=ctx, edit_function=imaging.polaroid, image=image, angle=angle, caption=caption, method="undefined")

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="rotate")
    async def rotate(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        degree: int = 45
    ) -> None:
        """
        Rotates the image an amount of degrees.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The amount of degrees to rotate the image.
        """

        self.limit(person=ctx.author, name="degree", value=degree, minimum=-360, maximum=360)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.rotate, image=image, degree=degree, reset_coords=True)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="sepia-tone", aliases=["sepia_tone", "sepiatone", "st"])
    async def sepia_tone(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        threshold: float = 0.8
    ) -> None:
        """
        Applies a filter that simulates chemical photography.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **threshold**: The factor to tone the image by.
        """

        self.limit(person=ctx.author, name="threshold", value=threshold, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.sepia_tone, image=image, threshold=threshold)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="solarize")
    async def solarize(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        threshold: float = 0.5
    ) -> None:
        """
        Replaces pixels above the threshold with negated ones.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **threshold**: Threshold to select pixels with.
        """

        self.limit(person=ctx.author, name="threshold", value=threshold, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.solarize, image=image, threshold=threshold)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="spread")
    async def spread(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        radius: float = 2.0,
        *,
        method: imaging.PixelInterpolateMethods = "undefined",
    ) -> None:
        """
        Replaces each pixel with one from the surrounding area.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **radius**: The area in which to search around a pixel to replace it with.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.spread, image=image, radius=radius, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="swirl")
    async def swirl(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        degree: int = 45,
        *,
        method: imaging.PixelInterpolateMethods = "undefined",
    ) -> None:
        """
        Swirls pixels around the center of the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        self.limit(person=ctx.author, name="degree", value=degree, minimum=-360, maximum=360)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.swirl, image=image, degree=degree, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="transparentize")
    async def transparentize(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        transparency: float = 0.5
    ) -> None:
        """
        Makes an image transparent.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The transparency of the new image, 0.0 being 0% and 1.0 being 100%.
        """

        self.limit(person=ctx.author, name="transparency", value=transparency, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.transparentize, image=image, transparency=transparency)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="wave")
    async def wave(
        self,
        ctx: custom.Context,
        image: Optional[objects.Image],
        *,
        method: imaging.PixelInterpolateMethods = "undefined",
    ) -> None:
        """
        Creates a wave like effect on the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.wave, image=image, method=method)
