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
            raise exceptions.ArgumentError('Can not get information for history that is 0 or smaller.')

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
            raise exceptions.ArgumentError('Can not get information for history that is 0 or smaller.')

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
            raise exceptions.ArgumentError('Can not get information for history that is 0 or smaller.')

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
        `all_servers`: Whether the graph should be all server or just this one.
        """

        if graph_type not in ('bar', 'pie'):
            raise exceptions.ArgumentError('That was not a valid graph type. Please choose either `pie` or `bar`.')

        async with ctx.channel.typing():
            plot = await self.bot.loop.run_in_executor(None, functools.partial(self.bot.imaging.do_guild_status_plot,
                                                                               ctx, graph_type, all_servers))
            return await ctx.send(file=discord.File(fp=plot, filename='GuildStatus.png'))

    @commands.cooldown(1, 30, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='floor')
    async def floor(self, ctx, url: str = None):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='floor')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='colorize', aliases=['colorise'])
    async def colorize(self, ctx, url: str = None, colour: str = None):

        async with ctx.channel.typing():

            if not colour:
                colour = self.bot.utils.random_colour()

            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='colorize', color=colour)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='solarize', aliases=['solarise'])
    async def solarize(self, ctx, url: str = None, threshold: float = 0.5):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='solarize', threshold=threshold)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='sketch')
    async def sketch(self, ctx, url: str = None, radius: float = 0.5, sigma: float = 0.0, angle: float = 98.0):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='sketch', radius=radius,
                                                            sigma=sigma, angle=angle)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='implode')
    async def implode(self, ctx, url: str = None, amount: float = 0.35):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='implode', amount=amount)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='sepiatone', aliases=['sepia_tone'])
    async def sepia_tone(self, ctx, url: str = None, threshold: float = 0.8):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='sepia_tone',
                                                            threshold=threshold)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='polaroid')
    async def polaroid(self, ctx, url: str = None, angle: float = 0.0, *, caption: str = None):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='polaroid', angle=angle,
                                                            caption=caption)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='vignette')
    async def vignette(self, ctx, url: str = None, sigma: float = 3, x: int = 10, y: int = 10):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='vignette', sigma=sigma,
                                                            x=x, y=y)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='swirl')
    async def swirl(self, ctx, url: str = None, degree: int = 90):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='swirl', degree=degree)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='charcoal')
    async def charcoal(self, ctx, url: str = None, radius: float = 1.5, sigma: float = 0.5):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='charcoal', radius=radius,
                                                            sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='noise')
    async def noise(self, ctx, url: str = None, method: str = 'gaussian', attenuate: float = 0.5):

        async with ctx.channel.typing():

            methods = ['gaussian', 'impulse', 'laplacian', 'multiplicative_gaussian', 'poisson', 'random', 'uniform']
            if method not in methods:
                return await ctx.send(f'That was not a valid method. Please use one of `gaussian`, `impulse`, '
                                      f'`laplacian`, `multiplicative_gaussian`, `poisson`, `random`, `uniform`')

            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='noise', method=method,
                                                            attenuate=attenuate)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='blueshift', aliases=['blue_shift'])
    async def blue_shift(self, ctx, url: str = None, factor: float = 1.25):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='blue_shift', factor=factor)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='spread')
    async def spread(self, ctx, url: str = None, radius: float = 5.0):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='spread', radius=radius)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='sharpen')
    async def sharpen(self, ctx, url: str = None, radius: float = 8, sigma: float = 4):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='sharpen', radius=radius,
                                                            sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='kuwahara')
    async def kuwahara(self, ctx, url: str = None, radius: float = 2, sigma: float = 1.5):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='kuwahara', radius=radius,
                                                            sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='emboss')
    async def emboss(self, ctx, url: str = None, radius: float = 3, sigma: float = 1.75):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='emboss', radius=radius,
                                                            sigma=sigma)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='edge')
    async def edge(self, ctx, url: str = None, radius: float = 1):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='edge', radius=radius)
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='flip')
    async def flip(self, ctx, url: str = None):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='flip')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='flop')
    async def flop(self, ctx, url: str = None):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='flop')
            return await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, commands.cooldowns.BucketType.guild)
    @commands.max_concurrency(1, per=commands.cooldowns.BucketType.guild)
    @commands.command(name='rotate')
    async def rotate(self, ctx, url: str = None, degree: int = 90):

        async with ctx.channel.typing():
            file, embed = await self.bot.imaging.edit_image(ctx=ctx, url=url, edit_type='rotate', degree=degree)
            return await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Images(bot))
