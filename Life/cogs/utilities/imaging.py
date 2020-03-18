import re
from io import BytesIO
from discord.ext import commands

import matplotlib.pyplot as plt
from wand.color import Color
from wand.image import Image

from cogs.utilities import exceptions


class Imaging:

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

        plot = BytesIO()
        plt.savefig(plot)
        plt.close()
        plot.seek(0)
        return plot

    def do_ping_plot(self, bot, history: int):

        times = [time for time, ping in list(bot.pings)[-history:]]
        pings = [ping for time, ping in list(bot.pings)[-history:]]
        lowest_pings = [index for index, ping in enumerate(pings) if ping == min(pings)]
        highest_pings = [index for index, ping in enumerate(pings) if ping == max(pings)]
        average_ping = round(sum([ping for ping in pings]) / len(pings), 2)

        plt.clf()
        plt.figure(figsize=(10, 6))

        plt.plot(times, pings, linewidth=1, c="navy", zorder=3)
        plt.plot(times, pings, markevery=lowest_pings, c="green", linewidth=0.0, marker="s", markersize=5, zorder=3)
        plt.plot(times, pings, markevery=highest_pings, c="red", linewidth=0.0, marker="s", markersize=5, zorder=3)
        plt.fill_between(range(len(pings)), pings, [min(pings) - 6] * len(pings), facecolor="navy", alpha=0.5, zorder=3)
        plt.text(0, min(pings) - 6, f"Average Ping: {average_ping}ms \nCurrent ping: {round(bot.latency * 1000)}ms \nLowest ping: {min(pings)}ms \nHighest ping: {max(pings)}ms")

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

        ping_graph = BytesIO()
        plt.savefig(ping_graph)
        plt.close()
        ping_graph.seek(0)
        return ping_graph

    async def get_image_url(self, ctx: commands.Context, argument: str):

        if not argument:
            argument = ctx.author.id

        try:
            member = await commands.MemberConverter().convert(ctx, str(argument))
            if member.is_avatar_animated() is True:
                argument = str(member.avatar_url_as(format="gif"))
            else:
                argument = str(member.avatar_url_as(format="png"))
        except commands.BadArgument:
            pass

        check_if_url = re.compile("(?:[^:/?#]+):?(?://[^/?#]*)?[^?#]*\.(?:jpg|gif|png|webp|jpeg)(?:\?[^#]*)?(?:#.*)?").match(argument)
        if check_if_url is None:
            raise exceptions.ArgumentError("You provided an invalid argument. Please provide an Image URL or a Members name, id or mention")

        return argument

    async def get_image(self, bot, url: str):
        async with bot.session.get(url) as response:
            image_bytes = await response.read()
        return image_bytes

    def colourise(self, image_bytes, image_colour: str):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        hex_check = re.compile("^#[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}$").match(image_colour)
        if hex_check is None:
            raise exceptions.ArgumentError("You provided an invalid colour format. Please use the format `#FFFFFF`.")

        with Color("rgb(50%, 50%, 50%)") as alpha:
            with Color(image_colour) as color:
                with Image(file=original_image) as image:
                    image_format = image.format
                    if image_format == "GIF":
                        with Image() as dest_image:
                            for frame in image.sequence:
                                frame.colorize(color=color, alpha=alpha)
                                dest_image.sequence.append(frame)
                            dest_image.save(file=new_image)
                    else:
                        image.colorize(color=color, alpha=alpha)
                        image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def implode(self, image_bytes, amount: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.implode(amount=amount)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.implode(amount=amount)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def sepia_tone(self, image_bytes, threshold: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.sepia_tone(threshold=threshold)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.sepia_tone(threshold=threshold)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def polaroid(self, image_bytes, angle: float, caption: str):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.polaroid(angle=angle, caption=caption)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.polaroid(angle=angle, caption=caption)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def vignette(self, image_bytes, sigma: float, x: int, y: int):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.vignette(sigma=sigma, x=x, y=y)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.vignette(sigma=sigma, x=x, y=y)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def swirl(self, image_bytes, degree: int):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.swirl(degree=degree)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.swirl(degree=degree)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def solarize(self, image_bytes, threshold: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.solarize(threshold=threshold * frame.quantum_range)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.solarize(threshold=threshold * image.quantum_range)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def sketch(self, image_bytes, radius: float, sigma: float, angle: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.sketch(radius=radius, sigma=sigma, angle=angle)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.sketch(radius=radius, sigma=sigma, angle=angle)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def charcoal(self, image_bytes, radius: float, sigma: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.charcoal(radius=radius, sigma=sigma)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.charcoal(radius=radius, sigma=sigma)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def noise(self, image_bytes, method: str, attenuate: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.noise(method, attenuate=attenuate)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.noise(method, attenuate=attenuate)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def blue_shift(self, image_bytes, factor: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.blue_shift(factor=factor)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.blue_shift(factor=factor)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def spread(self, image_bytes, radius: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.spread(radius=radius)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.spread(radius=radius)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def sharpen(self, image_bytes, radius: float, sigma: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.adaptive_sharpen(radius=radius, sigma=sigma)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.adaptive_sharpen(radius=radius, sigma=sigma)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def kuwahara(self, image_bytes, radius: float, sigma: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.kuwahara(radius=radius, sigma=sigma)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.kuwahara(radius=radius, sigma=sigma)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def emboss(self, image_bytes, radius: float, sigma: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.emboss(radius=radius, sigma=sigma)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.emboss(radius=radius, sigma=sigma)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def edge(self, image_bytes, radius: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.edge(radius=radius)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.edge(radius=radius)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def flip(self, image_bytes):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.flip()
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.flip()
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def flop(self, image_bytes):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.flop()
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.flop()
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def rotate(self, image_bytes, degree: float):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.rotate(degree=degree)
                        dest_image.sequence.append(frame)
                    dest_image.save(file=new_image)
            else:
                image.rotate(degree=degree)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

    def floor(self, image_bytes):

        original_image = BytesIO(image_bytes)
        new_image = BytesIO()

        with Image(file=original_image) as image:
            image_format = image.format
            if image_format == "GIF":
                with Image() as dest_image:
                    for frame in image.sequence:
                        frame.resize(100, 100)
                        frame.virtual_pixel = "tile"
                        arguments = (0, 0, 30, 50,
                                     100, 0, 70, 50,
                                     0, 100, 20, 100,
                                     100, 100, 80, 100)
                        frame.distort('perspective', arguments)
                        frame.resize(1000,1000)
                        dest_image.sequence.append(frame)

                    dest_image.save(file=new_image)
            else:
                image.resize(1000, 1000)
                image.virtual_pixel = "tile"
                arguments = (0,    0,     300, 500,
                             1000, 0,     700, 500,
                             0,    1000,  200, 1000,
                             1000, 1000,  800, 1000)
                image.distort('perspective', arguments)
                image.save(file=new_image)

        new_image.seek(0)
        return new_image, image_format

0