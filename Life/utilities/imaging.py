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


def do_pie_chart(values, names):
    plt.clf()

    labels = []
    percentages = []

    total = sum(values)

    for value in values:
        value = round(value / total * 100, 2)
        percentages.append(value)

    for name, percentage in zip(names, percentages):
        labels.append(f'{name}: {percentage}%')

    figure = plt.figure(1, figsize=(4, 3))

    axes = figure.add_subplot(111)
    axes.axis('equal')

    pie = axes.pie(values)

    box = axes.get_position()
    axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    axes.legend(pie[0], labels, loc="center left", fontsize=6, fancybox=True, bbox_to_anchor=(1, 0.5))

    pie_chart = BytesIO()
    plt.savefig(pie_chart, bbox_inches="tight", transparent=True)

    plt.close()

    pie_chart.seek(0)
    return pie_chart


def do_bar_chart(title, x_label, y_label, values, names):
    plt.clf()

    plt.bar(names, values, width=0.5, zorder=3)
    plt.grid(zorder=0)

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)

    plt.xticks(rotation=-90)

    plt.tight_layout()

    bar_chart = BytesIO()
    plt.savefig(bar_chart)

    plt.close()

    bar_chart.seek(0)
    return bar_chart


def do_plot(title, x_label, y_label, values, names):
    plt.clf()

    plt.plot(names, values, "-r", zorder=3)
    plt.grid(zorder=0)

    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)

    plt.xticks(rotation=-90)

    plt.tight_layout()

    plot = BytesIO()
    plt.savefig(plot)

    plt.close()

    plot.seek(0)
    return plot


def do_ping_graph(bot, history: int):

    times = [time for time, ping in list(bot.pings)[-history:]]
    pings = [ping for time, ping in list(bot.pings)[-history:]]
    lowest_pings = [index for index, ping in enumerate(pings) if ping == min(pings)]
    highest_pings = [index for index, ping in enumerate(pings) if ping == max(pings)]
    average_ping = round(sum([ping for time, ping in list(bot.pings)]) / len(bot.pings), 2)

    plt.clf()
    plt.figure(figsize=(10, 5))

    plt.plot(times, pings, linewidth=1, c="darkorange")
    plt.plot(times, pings, markevery=lowest_pings, c="green", linewidth=0.0, marker="s", markersize=5, zorder=3)
    plt.plot(times, pings, markevery=highest_pings, c="red", linewidth=0.0, marker="s", markersize=5, zorder=3)
    plt.fill_between(range(len(pings)), pings, [min(pings) - 10] * len(pings), facecolor="darkorange", alpha=0.5)
    plt.text(0.1, min(pings) - 9.9, f"Average Ping: {average_ping}ms \nCurrent ping: {round(bot.latency * 1000)}ms \nLowest ping: {min(pings)}ms \nHighest ping: {max(pings)}ms")

    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Ping (MS)")
    plt.xticks(rotation=-90)
    plt.grid(axis="y", which="both", zorder=1)

    plt.tick_params(axis="x", which="both", bottom=True if history <= 60 else False, labelbottom=True if history <= 60 else False)
    plt.minorticks_on()

    plt.tight_layout()

    ping_graph = BytesIO()
    plt.savefig(ping_graph)
    plt.close()
    ping_graph.seek(0)
    return ping_graph
