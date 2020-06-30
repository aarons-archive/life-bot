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

import functools
import re

import discord
from discord.ext import commands

from cogs.utilities import exceptions, imaging


class Images(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

        self.bot.image_url_regex = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:'
                                              'jpe?g|gif|png|webm))(?:\?([^#]*))?(?:#(.*))?')
        self.bot.hex_colour_regex = re.compile('^#[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}$')
        self.bot.imaging = imaging.Imaging(self.bot)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='user_graph', aliases=['ug'])
    async def user_graph(self, ctx, history: int = 24):
        """
        Display the bots user count over the past 24 hours.

        `history`: The amount of hours to display in the graph.
        """

        if history <= 0:
            raise exceptions.ArgumentError('History must be more than `0`.')

        async with ctx.channel.typing():

            query = 'WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date'
            user_growth = await self.bot.db.fetch(query, history)

            if not user_growth:
                return await ctx.send('No user growth data.')

            title = f'User growth over the last {len(user_growth)} hour(s)'
            y_axis = [record['member_count'] for record in user_growth]
            x_axis = [record['date'] for record in user_growth]

            plot = await self.bot.loop.run_in_executor(None, functools.partial(self.bot.imaging.do_growth_plot, title,
                                                                               'Datetime (YYYY-MM-DD: HH:MM)', 'Users',
                                                                               y_axis, x_axis))
            return await ctx.send(file=discord.File(fp=plot, filename='UserGraph.png'))

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='guild_graph', aliases=['gg'])
    async def guild_graph(self, ctx, history: int = 24):
        """
        Display the bots guild count over the past 24 hours.

        `history`: The amount of hours to display in the graph.
        """

        if history <= 0:
            raise exceptions.ArgumentError('History must be more than `0`.')

        async with ctx.channel.typing():

            query = 'WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date'
            guild_growth = await self.bot.db.fetch(query, history)

            if not guild_growth:
                return await ctx.send('No guild growth data.')

            title = f'Guild growth over the last {len(guild_growth)} hour(s)'
            y_axis = [record['guild_count'] for record in guild_growth]
            x_axis = [record['date'] for record in guild_growth]

            plot = await self.bot.loop.run_in_executor(None, functools.partial(self.bot.imaging.do_growth_plot, title,
                                                                               'Datetime (YYYY-MM-DD: HH:MM)', 'Guilds',
                                                                               y_axis, x_axis))
            return await ctx.send(file=discord.File(fp=plot, filename='GuildGraph.png'))

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='ping_graph', aliases=['pg'])
    async def ping_graph(self, ctx, history: int = 60):
        """
        Display the bot's latency over the last 60 minutes.

        `history`: The amount of minutes to display the graph.
        """

        if history <= 0:
            raise exceptions.ArgumentError('History must be more than `0`.')

        if not self.bot.pings:
            return await ctx.send('No ping data.')

        async with ctx.channel.typing():
            plot = await self.bot.loop.run_in_executor(None, functools.partial(self.bot.imaging.do_ping_plot, history))
            return await ctx.send(file=discord.File(fp=plot, filename='PingGraph.png'))

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='serverstatus', aliases=['ss'])
    async def serverstatus(self, ctx, graph_type: str = 'pie', all_servers=False):
        """
        Display member count per status in this server.

        `graph_type`: The graph type. Can be either `pie` or `bar`.
        `all_servers`: Whether the graph should be for all servers or just this one.
        """

        if graph_type not in ('bar', 'pie'):
            raise exceptions.ArgumentError('That was not a valid graph type. Please choose either `pie` or `bar`.')

        async with ctx.channel.typing():
            plot = await self.bot.loop.run_in_executor(None, functools.partial(self.bot.imaging.do_guild_status_plot,
                                                                               ctx, graph_type, all_servers))
            return await ctx.send(file=discord.File(fp=plot, filename='GuildStatus.png'))

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='blur')
    async def blur(self, ctx, image: str = None, amount: float = 2.0):
        """
        Blurs the given image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `amount`: The amount to blur the image by.
        """

        if amount < 0.0 or amount > 50.0:
            raise exceptions.ArgumentError('Amount must be between `0.0` and `50.0`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='blur', amount=amount)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='edge')
    async def edge(self, ctx, image: str = None, level: float = 1.0):
        """
        Converts the image to greyscale and detects edges.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `level`: The level of filter to apply to detect edges, best to be left at 1.
        """

        if level < 0 or level > 20:
            raise exceptions.ArgumentError('Level must be between `0` and `20`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='edge', level=level)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='emboss')
    async def emboss(self, ctx, image: str = None, radius: float = 3, sigma: float = 1.5):
        """
        Converts the image to greyscale and creates a 3d effect.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be lower than radius.
        """

        if radius < 0 or radius > 30:
            raise exceptions.ArgumentError('Radius must be between `0` and `30`.')
        if sigma < 0 or sigma > 30:
            raise exceptions.ArgumentError('Sigma must be between `0` and `30`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='emboss', radius=radius, sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='kuwahara')
    async def kuwahara(self, ctx, image: str = None, radius: float = 2, sigma: float = 1.5):
        """
        Smooths the given image while preserving edges.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `radius`: Filter aperture size.
        `sigma`: Filter standard deviation. Should be `0.5` lower than radius.
        """

        if radius < 0 or radius > 20:
            raise exceptions.ArgumentError('Radius must be between `0` and `20`.')

        if sigma < 0 or sigma > 20:
            raise exceptions.ArgumentError('Sigma must be between `0` and `20`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='kuwahara', radius=radius, sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='sharpen')
    async def sharpen(self, ctx, image: str = None, radius: float = 8, sigma: float = 4):
        """
        Sharpens the given image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be smaller than radius.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')

        if sigma < 0 or sigma > 50:
            raise exceptions.ArgumentError('Sigma must be between `0` and `50`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='sharpen', radius=radius, sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='spread')
    async def spread(self, ctx, image: str = None, radius: float = 2.0):
        """
        Replaces each pixel with one from the surrounding area.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `radius`: The area in which to search around a pixel to replace it with.
        """

        if radius < 0 or radius > 50:
            raise exceptions.ArgumentError('Radius must be between `0` and `50`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='spread', radius=radius)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='noise')
    async def noise(self, ctx, image: str = None, method: str = 'gaussian', attenuate: float = 0.5):
        """
        Adds random noise to the given image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `method`: The method to generate noise with.
        `attenuate`: The rate of noise distribution.
        """

        methods = ['uniform', 'gaussian', 'multiplicative_gaussian', 'impulse', 'laplacian', 'poisson', 'random']
        if method not in methods:
            return await ctx.send(f'`{method}` is not a valid method. Please use one of `uniform`, `gaussian`, '
                                  f'`multiplicative_gaussian`, `impulse`, `laplacian`, `poisson` or `random`.')

        if attenuate < 0 or attenuate > 1:
            raise exceptions.ArgumentError('Attenuate must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='noise', method=method, attenuate=attenuate)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='blueshift')
    async def blueshift(self, ctx, image: str = None, factor: float = 1.25):
        """
        Creates a moonlight effect by shifting blue colours.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `factor`: The factor to blue-shift colours by.
        """

        if factor < 0 or factor > 20:
            raise exceptions.ArgumentError('Factor must be be between `0` and `20`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='blueshift', factor=factor)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='charcoal')
    async def charcoal(self, ctx, image: str = None, radius: float = 1.5, sigma: float = 0.5):
        """
        Redraw the image as if it were drawn with charcoal.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `radius`: Filter aperture size. Should be larger than sigma.
        `sigma`: Filter standard deviation. Should be smaller than radius.
        """

        if radius < -10 or radius > 10:
            raise exceptions.ArgumentError('Radius must be between `-10.0` and `10.0`.')

        if sigma < -5 or sigma > 5:
            raise exceptions.ArgumentError('Sigma must be between `-5.0` and `5.0`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='charcoal', radius=radius, sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='colorize')
    async def colorize(self, ctx, image: str = None, color: str = None):
        """
        Colorizes the given image with a random color.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `colour`: The color to use. Must be formatted like `#FFFFFF`.
        """

        if not color:
            color = self.bot.utils.random_colour()

        if self.bot.hex_colour_regex.match(color) is None:
            raise exceptions.ArgumentError(f'The hex code `{color}` is invalid. Please use the format `#FFFFFF`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='colorize', color=color)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='implode')
    async def implode(self, ctx, image: str = None, amount: float = 0.4):
        """
        Pulls or pushes pixels from the center the image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `amount`: The factor to push or pull pixels by, negative values will push, positives will pull. Best results
        are -1.0 to 1.0.
        """

        if amount < -20 or amount > 20:
            raise exceptions.ArgumentError('Amount must be between `-20` and `20`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='implode', amount=amount)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='polaroid')
    async def polaroid(self, ctx, image: str = None, angle: float = 0.0, *, caption: str = None):
        """
        Puts the image in the center of a polaroid-like card.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `angle`: The angle that the polaroid will be rotated at.
        `caption`: A caption that will appear on the polaroid.
        """

        if angle < -360 or angle > 360:
            raise exceptions.ArgumentError('Angle must be between `-360` and `360`.')

        if caption and len(caption) > 100:
            raise exceptions.ArgumentError('Caption must be `100` characters or less.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='polaroid', angle=angle, caption=caption)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='sepiatone')
    async def sepia_tone(self, ctx, image: str = None, threshold: float = 0.8):
        """
        Applies a filter that simulates chemical photography.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `threshold`: The factor to tone the image by.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='sepiatone', threshold=threshold)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='solarize')
    async def solarize(self, ctx, image: str = None, threshold: float = 0.5):
        """
        Replaces pixels above the threshold with negated ones.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `threshold`: Threshold to select pixels with.
        """

        if threshold < 0 or threshold > 1:
            raise exceptions.ArgumentError('Threshold must be between `0.0` and `1.0`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image,
                                                            edit_type='solarize', threshold=threshold)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='swirl')
    async def swirl(self, ctx, image: str = None, degree: int = 45):
        """
        Swirls pixels around the center of the image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `degree`: The degree to swirl the pixels by, negative numbers will go clockwise and positives counter-clockwise.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='swirl', degree=degree)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='wave')
    async def wave(self, ctx, image: str = None):
        """
        Creates a wave like effect on the image.

        `image`: Can either be a direct image url, or a members name, id or mention.
        """

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='wave')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='flip')
    async def flip(self, ctx, image: str = None):
        """
        Flips the image along the x-axis.

        `image`: Can either be a direct image url, or a members name, id or mention.
        """

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='flip')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='flop')
    async def flop(self, ctx, image: str = None):
        """
        Flips the image along the y-axis.

        `image`: Can either be a direct image url, or a members name, id or mention.
        """

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='flop')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='rotate')
    async def rotate(self, ctx, image: str = None, degree: int = 45):
        """
        Rotates the image an amount of degrees.

        `image`: Can either be a direct image url, or a members name, id or mention.
        `degree`: The amount of degrees to rotate the image.
        """

        if degree < -360 or degree > 360:
            raise exceptions.ArgumentError('Degree must be between `-360` and `360`.')

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='rotate', degree=degree)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 30, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='floor')
    async def floor(self, ctx, image: str = None):
        """
        Warps and tiles the image which makes it like a floor.
        """

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, image=image, edit_type='floor')
            return await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Images(bot))
