from inspect import Parameter
from typing import Any, Literal, Optional

import discord
from discord.ext import commands

from core import colours, config, emojis
from core.bot import Life
from utilities import context, converters, exceptions, imaging, utils


_old_transform = commands.Command.transform


def _new_transform(self, ctx: context.Context, param: Parameter) -> Any:
    if param.annotation is Optional[converters.ImageConverter]:

        message = ctx.message
        if reference := ctx.message.reference:
            message = reference.cached_message or (reference.resolved if isinstance(reference.resolved, discord.Message) else ctx.message)

        default = None

        if attachments := message.attachments:
            default = attachments[0].url

        for embed in message.embeds:
            if (image := embed.image) or (image := embed.thumbnail):
                default = image.url
                break

        param = Parameter(
            name=param.name,
            kind=param.kind,
            default=default or utils.avatar(ctx.author),
            annotation=param.annotation
        )

    return _old_transform(self=self, ctx=ctx, param=param)


commands.Command.transform = _new_transform


def setup(bot: Life) -> None:
    bot.add_cog(Images(bot=bot))


class Images(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @staticmethod
    def limit(person: discord.User | discord.Member, name: str, value: float, minimum: float, maximum: float) -> None:

        if (minimum < value > maximum) and person.id not in config.OWNER_IDS:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{name}** must be between **{minimum}** and **{maximum}**."
            )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="blur")
    async def blur(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Blurs the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.blur, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="adaptive_blur", aliases=["ab"])
    async def adaptive_blur(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Blurs the image where there are no edges.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.adaptive_blur, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="sharpen")
    async def sharpen(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Sharpens the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.sharpen, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="adaptive_sharpen", aliases=["as"])
    async def adaptive_sharpen(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 10,
        sigma: float = 5
    ) -> None:
        """
        Sharpens the image where edges are detected.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.adaptive_sharpen, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="blueshift", aliases=["blue-shift", "blue_shift", "bs"])
    async def blueshift(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        factor: float = 1.25
    ) -> None:
        """
        Creates a night time moonlight effect by shifting blue colour values.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **factor**: The factor to shift blue colour values by.
        """

        self.limit(person=ctx.author, name="factor", value=factor, minimum=0, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.blueshift, url=str(image), factor=factor)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="border")
    async def border(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        colour: commands.ColourConverter = utils.MISSING,
        width: int = 20,
        height: int = 20
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
            url=str(image),
            colour=str(colour) if colour else utils.random_hex(),
            width=width,
            height=height
        )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="colorize", aliases=["colourize", "colorise", "colourise"])
    async def colorize(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
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

        await imaging.edit_image(ctx=ctx, edit_function=imaging.colorize, url=str(image), colour=str(colour) if colour else utils.random_hex())

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="despeckle")
    async def despeckle(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Removes noise from an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.despeckle, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="floor")
    async def floor(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Warps and tiles the image which makes it like a floor.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.floor, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="emboss")
    async def emboss(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 3,
        sigma: float = 1
    ) -> None:
        """
        Creates a 3D effect within the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.emboss, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="enhance")
    async def enhance(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Removes noise from an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.enhance, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="flip")
    async def flip(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Flips the image along the x-axis.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.flip, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="flop")
    async def flop(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Flips the image along the y-axis.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.flop, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="frame")
    async def frame(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        colour: Optional[commands.ColourConverter],
        width: int = 20,
        height: int = 20,
        inner: int = 5,
        outer: int = 10
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
            url=str(image),
            matte=str(colour) if colour else utils.random_hex(),
            height=height,
            width=width,
            inner_bevel=inner,
            outer_bevel=outer
        )

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="implode", aliases=["explode"])
    async def implode(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        factor: float = 0.4,
        *,
        method: imaging.PixelInterpolateMethods = "undefined"
    ) -> None:
        """
        Pulls or pushes pixels from the center the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        **factor**: The factor to push or pull pixels by, negative values will push, positives will pull. For the best results use -1.0 to 1.0.
        """

        self.limit(person=ctx.author, name="factor", value=factor, minimum=-20, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.implode, url=str(image), amount=factor, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="kmeans")
    async def kmeans(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        colors: int = 10
    ) -> None:
        """
        Reduces the amount of colours in an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        **colors**: The amount of colours to keep in the image.
        """

        self.limit(person=ctx.author, name="colours", value=colors, minimum=0, maximum=1024)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.kmeans, url=str(image), number_colours=colors)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="kuwahara")
    async def kuwahara(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 5,
        sigma: float = 2.5
    ) -> None:
        """
        Smooths the given image while preserving edges.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=20)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=20)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.kuwahara, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="motionblur", aliases=["motion-blur", "motion_blue", "mb"])
    async def motion_blur(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 30,
        sigma: float = 20,
        angle: int = 90
    ) -> None:
        """
        Applies a blur along an angle.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=50)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=50)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.motion_blur, url=str(image), radius=radius, sigma=sigma, angle=angle)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="invert", aliases=["negate"])
    async def invert(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Inverts the colours in an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.negate, url=str(image))

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="noise")
    async def noise(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        attenuate: float = 0.5,
        method: imaging.NoiseTypes = "impulse"
    ) -> None:
        """
        Adds random noise to an image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **attenuate**: The rate of noise distribution.
        **method**: The method to generate noise with.

        Methods: **undefined**, **uniform**, **gaussian**, **multiplicative_gaussian**, **impulse**, **laplacian**, **poisson**, **random**.
        """

        self.limit(person=ctx.author, name="attenuate", value=attenuate, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.noise, url=str(image), method=method, attenuate=attenuate)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="oil_paint", aliases=["op"])
    async def oil_paint(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 2,
        sigma: float = 1
    ) -> None:
        """
        Edits the image to look like an oil painting.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)
        self.limit(person=ctx.author, name="sigma", value=sigma, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.oil_paint, url=str(image), radius=radius, sigma=sigma)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="polaroid")
    async def polaroid(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
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

        await imaging.edit_image(ctx=ctx, edit_function=imaging.polaroid, url=str(image), angle=angle, caption=caption, method="undefined")

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="rotate")
    async def rotate(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        degree: int = 45
    ) -> None:
        """
        Rotates the image an amount of degrees.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The amount of degrees to rotate the image.
        """

        self.limit(person=ctx.author, name="degree", value=degree, minimum=-360, maximum=360)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.rotate, url=str(image), degree=degree, reset_coords=True)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="sepia_tone", aliases=["st"])
    async def sepia_tone(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        threshold: float = 0.8
    ) -> None:
        """
        Applies a filter that simulates chemical photography.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **threshold**: The factor to tone the image by.
        """

        self.limit(person=ctx.author, name="threshold", value=threshold, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.sepia_tone, url=str(image), threshold=threshold)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="solarize")
    async def solarize(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        threshold: float = 0.5
    ) -> None:
        """
        Replaces pixels above the threshold with negated ones.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **threshold**: Threshold to select pixels with.
        """

        self.limit(person=ctx.author, name="threshold", value=threshold, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.solarize, url=str(image), threshold=threshold)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="spread")
    async def spread(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        radius: float = 2.0,
        *,
        method: imaging.PixelInterpolateMethods = "undefined"
    ) -> None:
        """
        Replaces each pixel with one from the surrounding area.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **radius**: The area in which to search around a pixel to replace it with.
        """

        self.limit(person=ctx.author, name="radius", value=radius, minimum=0, maximum=30)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.spread, url=str(image), radius=radius, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="swirl")
    async def swirl(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        degree: int = 45,
        *,
        method: imaging.PixelInterpolateMethods = "undefined"
    ) -> None:
        """
        Swirls pixels around the center of the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        self.limit(person=ctx.author, name="degree", value=degree, minimum=-360, maximum=360)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.swirl, url=str(image), degree=degree, method=method)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="transparentize")
    async def transparentize(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        transparency: float = 0.5
    ) -> None:
        """
        Makes an image transparent.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.

        **degree**: The transparency of the new image, 0.0 being 0% and 1.0 being 100%.
        """

        self.limit(person=ctx.author, name="transparency", value=transparency, minimum=0.0, maximum=1.0)

        await imaging.edit_image(ctx=ctx, edit_function=imaging.transparentize, url=str(image), transparency=transparency)

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="wave")
    async def wave(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        *,
        method: imaging.PixelInterpolateMethods = "undefined"
    ) -> None:
        """
        Creates a wave like effect on the image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.wave, url=str(image), method=method)

    # In development commands.

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="cube")
    async def cube(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Creates a cube from the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.cube, url=str(image), filename=f"{ctx.author}")

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="sphere")
    async def sphere(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Turns the given image into a sphere.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.sphere, url=str(image), filename=f"{ctx.author}")

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="tshirt", aliases=["shirt"])
    async def tshirt(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter]
    ) -> None:
        """
        Creates a tshirt with the given image.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.tshirt, url=str(image), filename=f"{ctx.author}")

    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.member)
    @commands.command(name="pixel")
    async def pixel(
        self,
        ctx: context.Context,
        image: Optional[converters.ImageConverter],
        *,
        method: Literal["square", "s", "hexagon", "h", "random", "r"] = "random"
    ) -> None:
        """
        Turns the image into a pixel art.

        **image**: Can be a members ID, Username, Nickname or @Mention, attachment, emoji or image url.
        """

        await imaging.edit_image(ctx=ctx, edit_function=imaging.pixel, url=str(image), filename=f"{ctx.author}", method=method)
