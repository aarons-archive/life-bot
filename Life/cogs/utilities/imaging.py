import functools
import io
import multiprocessing
import re
import typing

import matplotlib.pyplot as plt
from discord.ext import commands
from wand.color import Color
from wand.image import Image
from wand.sequence import SingleImage

from cogs.utilities import exceptions


def floor(image: typing.Union[Image, SingleImage]):

    image.sample(1000, 1000)
    image.virtual_pixel = "tile"
    arguments = (0,            0,           300, 600,
                 image.height, 0,           700, 600,
                 0,            image.width, 200, 1000,
                 image.height, image.width, 800, 1000)
    image.distort('perspective', arguments)

def colorize(image: typing.Union[Image, SingleImage], color: str):

    hex_check = re.compile("^#[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}$").match(color)
    if hex_check is None:
        raise exceptions.ArgumentError("You provided an invalid colour format. Please use the format `#FFFFFF`.")

    with Color(color) as image_color:
        with Color("rgb(50%, 50%, 50%)") as image_alpha:
            image.colorize(color=image_color, alpha=image_alpha)

def solarize(image: typing.Union[Image, SingleImage], threshold: float):

    image.solarize(threshold=threshold * image.quantum_range)

def sketch(image: typing.Union[Image, SingleImage], radius: float, sigma: float, angle: float):

    image.sketch(radius=radius, sigma=sigma, angle=angle)

def implode(image: typing.Union[Image, SingleImage], amount: float):

    image.implode(amount=amount)

def sepia_tone(image: typing.Union[Image, SingleImage], threshold: float):

    image.sepia_tone(threshold=threshold)

def polaroid(image: typing.Union[Image, SingleImage], angle: float, caption: str):

    image.polaroid(angle=angle, caption=caption)

def vignette(image: typing.Union[Image, SingleImage], sigma: float, x: int, y: int):

    image.vignette(sigma=sigma, x=x, y=y)

def swirl(image: typing.Union[Image, SingleImage], degree: int):

    image.swirl(degree=degree)

def charcoal(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.charcoal(radius=radius, sigma=sigma)

def noise(image: typing.Union[Image, SingleImage], method: str, attenuate: float):

    image.noise(method, attenuate=attenuate)

def blue_shift(image: typing.Union[Image, SingleImage], factor: float):

    image.blue_shift(factor=factor)

def spread(image: typing.Union[Image, SingleImage], radius: float):

    image.spread(radius=radius)

def sharpen(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.adaptive_sharpen(radius=radius, sigma=sigma)

def kuwahara(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.kuwahara(radius=radius, sigma=sigma)

def emboss(image: typing.Union[Image, SingleImage], radius: float, sigma: float):

    image.emboss(radius=radius, sigma=sigma)

def edge(image: typing.Union[Image, SingleImage], radius: float):

    image.edge(radius=radius)

def flip(image: typing.Union[Image, SingleImage]):

    image.flip()

def flop(image: typing.Union[Image, SingleImage]):

    image.flop()

def rotate(image: typing.Union[Image, SingleImage], degree: float):

    image.rotate(degree=degree)
    
    
image_operations = {
    "floor": floor,
    "colorize": colorize,
    "solarize": solarize,
    "sketch": sketch,
    "implode": implode,
    "sepia_tone": sepia_tone,
    "polaroid": polaroid,
    "vignette": vignette,
    "swirl": swirl,
    "charcoal": charcoal,
    "noise": noise,
    "blue_shift": blue_shift,
    "spread": spread,
    "sharpen": sharpen,
    "kuwahara": kuwahara,
    "emboss": emboss,
    "edge": edge,
    "flip": flip,
    "flop": flop,
    "rotate": rotate,
}


def do_edit_image(edit_function, image_bytes: bytes, queue: multiprocessing.Queue, **kwargs):

    original_image = io.BytesIO(image_bytes)
    edited_image = io.BytesIO()

    with Image(file=original_image) as image:
        image_format = image.format
        if image_format == "GIF":
            with Image() as new_image:
                for frame in image.sequence:
                    edit_function(frame, **kwargs)
                    new_image.sequence.append(frame)
                new_image.save(file=edited_image)
        else:
            edit_function(image, **kwargs)
            image.save(file=edited_image)

    edited_image.seek(0)
    queue.put((edited_image, image_format))


class Imaging:

    def __init__(self, bot):
        self.bot = bot

        self.queue = multiprocessing.Queue()

    async def get_image_url(self, ctx: commands.Context, argument: str):

        if not argument:
            argument = ctx.author.id

        try:
            member = await commands.MemberConverter().convert(ctx, str(argument))
            argument = str(member.avatar_url_as(format="gif" if member.is_avatar_animated() is True else "png"))
        except commands.BadArgument:
            pass

        check_if_url = re.compile("(?:[^:/?#]+):?(?://[^/?#]*)?[^?#]*\.(?:|gif|png)(?:\?[^#]*)?(?:#.*)?").match(argument)
        if check_if_url is None:
            raise exceptions.ArgumentError("You provided an invalid argument. Please provide an Image URL or a Members name, id or mention")

        return argument

    async def get_image_bytes(self, url: str):

        async with self.bot.session.get(url) as response:
            image_bytes = await response.read()
        return image_bytes

    async def edit_image(self, ctx: commands.Context, url: str, edit_type: str, **kwargs):

        if edit_type not in image_operations.keys():
            raise exceptions.ArgumentError(f"'{edit_type}' is not a valid image operation")

        edit_function = image_operations[edit_type]
        image_url = await self.get_image_url(ctx=ctx, argument=url)
        image_bytes = await self.get_image_bytes(url=image_url)

        process = multiprocessing.Process(target=do_edit_image, args=(edit_function, image_bytes, self.queue), kwargs=kwargs, daemon=True)
        process.start()

        function = functools.partial(self.queue.get)

        edited_image, image_format = await self.bot.loop.run_in_executor(None, function)
        return edited_image, image_format

    def do_ping_plot(self, history: int):

        times = [time for time, ping in list(self.bot.pings)[-history:]]
        pings = [ping for time, ping in list(self.bot.pings)[-history:]]
        lowest_pings = [index for index, ping in enumerate(pings) if ping == min(pings)]
        highest_pings = [index for index, ping in enumerate(pings) if ping == max(pings)]
        average_ping = round(sum([ping for ping in pings]) / len(pings), 2)

        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(times, pings, linewidth=1, c="navy", zorder=3)
        plt.plot(times, pings, markevery=lowest_pings, c="green", linewidth=0.0, marker="s", markersize=5, zorder=3)
        plt.plot(times, pings, markevery=highest_pings, c="red", linewidth=0.0, marker="s", markersize=5, zorder=3)
        plt.fill_between(range(len(pings)), pings, [min(pings) - 6] * len(pings), facecolor="navy", alpha=0.5, zorder=3)
        plt.text(0, min(pings) - 6, f"Average Ping: {average_ping}ms \nCurrent ping: {round(self.bot.latency * 1000)}ms \nLowest ping: {min(pings)}ms \nHighest ping: {max(pings)}ms")

        plt.xlabel("Time (HH:MM)")
        plt.ylabel("Ping (MS)")
        plt.title(f"Ping over the last {len(pings)} minutes(s)")
        plt.xticks(rotation=-90)

        if len(pings) <= 180:
            plt.minorticks_on()
            plt.grid(axis="x", zorder=1)

        plt.grid(axis="y", which="both", zorder=1)
        plt.tick_params(axis="x", which="major", bottom=True if len(pings) <= 60 else False, labelbottom=True if len(pings) <= 60 else False)
        plt.tick_params(axis="x", which="minor", bottom=False)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer)
        plt.close()

        buffer.seek(0)
        return buffer

    def do_growth_plot(self, title: str, x_label: str, y_label: str, values: list, names: list):

        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(names, values, color="navy", zorder=3)

        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)
        plt.xticks(rotation=-90)

        if len(values) <= 168:
            plt.minorticks_on()
            plt.grid(axis="x", zorder=1)

        plt.grid(axis="y", which="both", zorder=1)
        plt.tick_params(axis="x", which="major", bottom=True if len(values) <= 72 else False, labelbottom=True if len(values) <= 72 else False)
        plt.tick_params(axis="x", which="minor", bottom=False)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer)
        plt.close()

        buffer.seek(0)
        return buffer

    def do_status_plot(self, ctx: commands.Context, graph_type: str, all_guilds: bool = False):
        
        buffer = io.BytesIO()
        online_count, idle_count, dnd_count, offline_count, streaming_count = self.bot.utils.guild_user_status(ctx.guild, all_guilds=all_guilds)
        total = online_count + idle_count + dnd_count + offline_count

        if graph_type == "pie":
        
            online_percent = round((online_count / total) * 100, 2)
            idle_percent = round((idle_count / total) * 100, 2)
            dnd_percent = round((dnd_count / total) * 100, 2)
            offline_percent = round((offline_count / total) * 100, 2)
            streaming_percent = round((streaming_count / total) * 100, 2)
    
            labels = [f"{online_percent}%", f"{idle_percent}%", f"{dnd_percent}%", f"{offline_percent}%", f"{streaming_percent}%"]
            sizes = [online_count, idle_count, dnd_count, offline_count, streaming_count]
            colors = ["#7acba6", "#fcc15d", "#f57e7e", "#9ea4af", "#593695"]
            
            plt.clf()
            figure, axes = plt.subplots(figsize=(6, 4), subplot_kw=dict(aspect="equal"))
            
            axes.pie(sizes, colors=colors, startangle=90)
            axes.legend(labels, loc="center right", title="Status's")
            
            if all_guilds is True:
                axes.set_title(f"Percentage of members per status across all guilds.")
            else:
                axes.set_title(f"Percentage of members per status in {ctx.guild.name}")

            axes.axis("equal")
            plt.tight_layout()
            
            plt.savefig(buffer)
            plt.close()
            
        if graph_type == "bar":
            
            labels = ["Online", "Idle", "DnD", "Offline", "Streaming"]
            values = [online_count, idle_count, dnd_count, offline_count, streaming_count]
            colors = ["#7acba6", "#fcc15d", "#f57e7e", "#9ea4af", "#593695"]

            plt.clf()
            plt.figure(figsize=(6, 4))

            bar_chart = plt.bar(labels, values, color=colors, zorder=3)
            if all_guilds is True:
                plt.title(f"Member count per status across all guilds.")
            else:
                plt.title(f"Members count per status in {ctx.guild.name}")
            plt.ylabel("Member count")
            plt.xlabel("Status")

            for bar in bar_chart:
                height = bar.get_height()
                plt.annotate('{}'.format(height), xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 2), textcoords="offset points", ha='center')
                
            plt.minorticks_on()
            plt.grid(which="both", axis="y", zorder=0)
            
            plt.tight_layout()
            
            plt.savefig(buffer)
            plt.close()
            
        buffer.seek(0)
        return buffer

