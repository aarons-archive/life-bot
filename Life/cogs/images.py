import time

import discord
from discord.ext import commands


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def create_embed(self, image, image_format: str):
        file = discord.File(filename=f"EditedImage.{image_format.lower()}", fp=image)
        embed = discord.Embed(
            colour=discord.Colour.gold(),
        )
        embed.set_image(url=f"attachment://EditedImage.{image_format.lower()}")
        return file, embed

    @commands.cooldown(1, 60, commands.cooldowns.BucketType.guild)
    @commands.command(name="user_growth", aliases=["ug"])
    async def user_growth(self, ctx, history: int = 24):
        """
        Show the bot's user count over the past 24 (by default) hours.

        `history`: The amount of hours to get the user count of.
        """

        user_growth = await self.bot.db.fetch("WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date", history)

        if not user_growth:
            return await ctx.send("No growth data.")

        start = time.perf_counter()
        plot = self.bot.imaging.do_growth_plot(f"User growth over the last {len(user_growth)} hour(s)", "Datetime (YYYY-MM-DD: HH:MM)", "Users", [record["member_count"] for record in user_growth], [record["date"] for record in user_growth])
        await ctx.send(file=discord.File(filename=f"UserGrowth.png", fp=plot))
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.cooldown(1, 60, commands.cooldowns.BucketType.guild)
    @commands.command(name="guild_growth", aliases=["gg"])
    async def guild_growth(self, ctx, history: int = 24):
        """
        Show the bot's guild count over the past 24 (by default) hours.

        `history`: The amount of hours to get the guild count of.
        """

        guild_growth = await self.bot.db.fetch("WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date", history)

        if not guild_growth:
            return await ctx.send("No growth data.")

        start = time.perf_counter()
        plot = self.bot.imaging.do_growth_plot(f"Guild growth over the last {len(guild_growth)} hour(s)", "Datetime (YYYY-MM-DD: HH:MM)", "Guilds", [record["guild_count"] for record in guild_growth], [record["date"] for record in guild_growth])
        await ctx.send(file=discord.File(filename=f"GuildGrowth.png", fp=plot))
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.cooldown(1, 60, commands.cooldowns.BucketType.guild)
    @commands.command(name="ping_graph", aliases=["pg"])
    async def ping_graph(self, ctx, history: int = 60):
        """
        Show the bot's latency over the last 60 (by default) minutes.

        `history`: The amount of minutes to get the latency of.
        """

        if not self.bot.pings:
            return await ctx.send("No ping data.")

        start = time.perf_counter()
        await ctx.trigger_typing()
        plot = self.bot.imaging.do_ping_plot(self.bot, history=history)
        await ctx.send(file=discord.File(filename=f"PingGraph.png", fp=plot))
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.command(name="colour", aliases=["color"])
    async def colour(self, ctx, url: str = None, colour: str = None):

        await ctx.trigger_typing()

        if not colour:
            colour = self.bot.utils.random_colour()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.colourise(image_bytes=image_bytes, image_colour=colour)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Colour: {colour}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="implode")
    async def implode(self, ctx, url: str = None, amount: float = 0.35):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.implode(image_bytes=image_bytes, amount=amount)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Amount: {amount}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="sepiatone", aliases=["sepia_tone"])
    async def sepia_tone(self, ctx, url: str = None, threshold: float = 0.8):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.sepia_tone(image_bytes=image_bytes, threshold=threshold)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Threshold: {threshold}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="polaroid")
    async def polaroid(self, ctx, url: str = None, angle: float = 0.0, *, caption: str = None):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.polaroid(image_bytes=image_bytes, angle=angle, caption=caption)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Angle: {angle} | Caption: {caption}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="vignette")
    async def vignette(self, ctx, url: str = None, sigma: float = 3, x: int = 10, y: int = 10):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.vignette(image_bytes=image_bytes, sigma=sigma, x=x, y=y)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Sigma: {sigma} | X: {x} | Y: {y}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="swirl")
    async def swirl(self, ctx, url: str = None, degree: int = 90):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.swirl(image_bytes=image_bytes, degree=degree)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Degree: {degree}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="solarize", aliases=["solarise"])
    async def solarize(self, ctx, url: str = None, threshold: float = 0.5):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.solarize(image_bytes=image_bytes, threshold=threshold)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Threshold: {threshold}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="sketch")
    async def sketch(self, ctx, url: str = None, radius: float = 0.5, sigma: float = 0.0, angle: float = 98.0):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.sketch(image_bytes=image_bytes, radius=radius, sigma=sigma, angle=angle)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma} | Angle: {angle}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="charcoal")
    async def charcoal(self, ctx, url: str = None, radius: float = 1.5, sigma: float = 0.5):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.charcoal(image_bytes=image_bytes, radius=radius, sigma=sigma)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="noise")
    async def noise(self, ctx, url: str = None, method: str = "gaussian", attenuate: float = 0.5):

        await ctx.trigger_typing()

        methods = ["gaussian", "impulse", "laplacian", "multiplicative_gaussian", "poisson", "random", "uniform"]
        if method not in methods:
            return await ctx.send(f"That was not a valid method. Please use one of `gaussian`, `impulse`, `laplacian`, "
                                  f"`multiplicative_gaussian`, `poisson`, `random`, `uniform`")

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.noise(image_bytes=image_bytes, method=method, attenuate=attenuate)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Method: {method} | Attenuate: {attenuate}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="blueshift", aliases=["blue_shift"])
    async def noise(self, ctx, url: str = None, factor: float = 1.25):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.blue_shift(image_bytes=image_bytes, factor=factor)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Factor: {factor}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="spread")
    async def spread(self, ctx, url: str = None, radius: float = 5.0):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.spread(image_bytes=image_bytes, radius=radius)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="sharpen")
    async def sharpen(self, ctx, url: str = None, radius: float = 8, sigma: float = 4):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.sharpen(image_bytes=image_bytes, radius=radius, sigma=sigma)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma}")
        return await ctx.send(file=file, embed=embed)#

    @commands.command(name="kuwahara")
    async def kuwahara(self, ctx, url: str = None, radius: float = 2, sigma: float = 1.5):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.kuwahara(image_bytes=image_bytes, radius=radius, sigma=sigma)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="emboss")
    async def emboss(self, ctx, url: str = None, radius: float = 3, sigma: float = 1.75):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.emboss(image_bytes=image_bytes, radius=radius, sigma=sigma)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius} | Sigma: {sigma}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="edge")
    async def edge(self, ctx, url: str = None, radius: float = 1):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.edge(image_bytes=image_bytes, radius=radius)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Radius: {radius}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="flip")
    async def flip(self, ctx, url: str = None):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.flip(image_bytes=image_bytes)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="flop")
    async def flop(self, ctx, url: str = None):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.flop(image_bytes=image_bytes)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="rotate")
    async def rotate(self, ctx, url: str = None, degree: int = 90):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.rotate(image_bytes=image_bytes, degree=degree)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        embed.set_footer(text=f"Degree: {degree}")
        return await ctx.send(file=file, embed=embed)

    @commands.command(name="floor")
    async def floor(self, ctx, url: str = None):

        await ctx.trigger_typing()

        image_bytes = await self.bot.imaging.get_image(self.bot, await self.bot.imaging.get_image_url(ctx=ctx, argument=url))
        image, image_format = self.bot.imaging.floor(image_bytes=image_bytes)

        file, embed = await self.create_embed(image=image, image_format=image_format)
        return await ctx.send(file=file, embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))
