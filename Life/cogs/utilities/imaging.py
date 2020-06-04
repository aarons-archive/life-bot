import functools
import io
import multiprocessing
import typing

import discord
import matplotlib.pyplot as plt
from discord.ext import commands
from wand.color import Color
from wand.image import Image
from wand.sequence import SingleImage
from wand.exceptions import *

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
                new_image.save(file=image_edited)
            else:
                new_image, image_text = edit_function(old_image, **kwargs)
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

    def do_ping_plot(self, history: int):

        buffer = io.BytesIO()

        times = [time for time, ping in list(self.bot.pings)[-history:]]
        pings = [ping for time, ping in list(self.bot.pings)[-history:]]
        lowest_pings = [index for index, ping in enumerate(pings) if ping == min(pings)]
        highest_pings = [index for index, ping in enumerate(pings) if ping == max(pings)]
        average_ping = round(sum([ping for ping in pings]) / len(pings), 2)

        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(times, pings, linewidth=1, c='navy', zorder=3)
        plt.plot(times, pings, markevery=lowest_pings, c='green', linewidth=0.0, marker='s', markersize=5, zorder=3)
        plt.plot(times, pings, markevery=highest_pings, c='red', linewidth=0.0, marker='s', markersize=5, zorder=3)
        plt.fill_between(range(len(pings)), pings, [min(pings) - 6] * len(pings), facecolor='navy', alpha=0.5, zorder=3)
        plt.text(0, min(pings) - 6, f'Average Ping: {average_ping}ms \n'
                                    f'Current ping: {round(self.bot.latency * 1000)}ms \n'
                                    f'Lowest ping: {min(pings)}ms \n'
                                    f'Highest ping: {max(pings)}ms')

        plt.xlabel('Time (HH:MM)')
        plt.ylabel('Ping (MS)')
        plt.title(f'Ping over the last {len(pings)} minutes(s)')
        plt.xticks(rotation=-90)

        if len(pings) <= 180:
            plt.minorticks_on()
            plt.grid(axis='x', zorder=1)

        plt.grid(axis='y', which='both', zorder=1)
        plt.tick_params(axis='x', which='major', bottom=True if len(pings) <= 60 else False,
                        labelbottom=True if len(pings) <= 60 else False)
        plt.tick_params(axis='x', which='minor', bottom=False)
        plt.tight_layout()

        plt.savefig(buffer)
        plt.close()

        buffer.seek(0)
        return buffer

    def do_growth_plot(self, title: str, x_label: str, y_label: str, values: list, names: list):

        buffer = io.BytesIO()

        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(names, values, color='navy', zorder=3)

        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)
        plt.xticks(rotation=-90)

        if len(values) <= 168:
            plt.minorticks_on()
            plt.grid(axis='x', zorder=1)

        plt.grid(axis='y', which='both', zorder=1)
        plt.tick_params(axis='x', which='major', bottom=True if len(values) <= 72 else False,
                        labelbottom=True if len(values) <= 72 else False)
        plt.tick_params(axis='x', which='minor', bottom=False)
        plt.tight_layout()

        plt.savefig(buffer)
        plt.close()

        buffer.seek(0)
        return buffer

    def do_guild_status_plot(self, ctx: commands.Context, graph_type: str, all_guilds: bool = False):

        buffer = io.BytesIO()

        statuses = self.bot.utils.guild_member_status(guild=ctx.guild, all_guilds=all_guilds)
        total = sum(statuses.values())
        online = statuses['online']
        idle = statuses['idle']
        dnd = statuses['dnd']
        offline = statuses['offline']
        streaming = statuses['streaming']

        if graph_type == 'pie':

            online_percent = round((online / total) * 100, 2)
            idle_percent = round((idle / total) * 100, 2)
            dnd_percent = round((dnd / total) * 100, 2)
            offline_percent = round((offline / total) * 100, 2)
            streaming_percent = round((streaming / total) * 100, 2)

            labels = [f'{online_percent}%', f'{idle_percent}%', f'{dnd_percent}%', f'{offline_percent}%',
                      f'{streaming_percent}%']
            sizes = [online, idle, dnd, offline, streaming]
            colors = ['#7acba6', '#fcc15d', '#f57e7e', '#9ea4af', '#593695']

            plt.clf()
            figure, axes = plt.subplots(figsize=(6, 4), subplot_kw=dict(aspect='equal'))

            axes.pie(sizes, colors=colors, startangle=90)
            axes.legend(labels, loc='center right', title="Status's", frameon=False)

            if all_guilds is True:
                axes.set_title(f'Percentage of members per status across all guilds.')
            else:
                axes.set_title(f'Percentage of members per status in {ctx.guild.name}')

            axes.axis('equal')
            plt.tight_layout()

            plt.savefig(buffer)
            plt.close()

        if graph_type == 'bar':

            labels = ['Online', 'Idle', 'DnD', 'Offline', 'Streaming']
            values = [online, idle, dnd, offline, streaming]
            colors = ['#7acba6', '#fcc15d', '#f57e7e', '#9ea4af', '#593695']

            plt.clf()
            plt.figure(figsize=(6, 4))

            bar_chart = plt.bar(labels, values, color=colors, zorder=3)
            if all_guilds is True:
                plt.title(f'Member count per status across all guilds.')
            else:
                plt.title(f'Members count per status in {ctx.guild.name}')
            plt.ylabel('Member count')
            plt.xlabel('Status')

            for bar in bar_chart:
                height = bar.get_height()
                plt.annotate('{}'.format(height), xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 2),
                             textcoords='offset points', ha='center')

            plt.minorticks_on()
            plt.grid(which='both', axis='y', zorder=0)

            plt.tight_layout()

            plt.savefig(buffer)
            plt.close()

        buffer.seek(0)
        return buffer
