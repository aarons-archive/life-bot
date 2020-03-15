from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image


async def get_image(bot, url):
    async with bot.session.get(url) as response:
        image_bytes = await response.read()
    return image_bytes


def colour(image_bytes, image_colour):
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    mask = image.convert("L")

    lx, ly = image.size
    pixel = image.load()
    for y in range(ly):
        for x in range(lx):
            if pixel[x, y] == (0, 0, 0, 0):
                continue
            pixel[x, y] = image_colour

    image.putalpha(mask)

    colour_image = BytesIO()
    image.save(colour_image, "png")

    image.close()
    mask.close()

    colour_image.seek(0)
    return colour_image


def do_growth_plot(title, x_label, y_label, values, names):

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


def do_ping_plot(bot, history: int):

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
