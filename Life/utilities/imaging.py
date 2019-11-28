from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image


async def get_image(bot, url):
    async with bot.session.get(url) as response:
        image_bytes = await response.read()
    return image_bytes

def colour(image_bytes, image_colour):

    # Open the image_bytes as an image, and convert it to an RGBA type image.
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    mask = image.convert("L")

    # Switch pixels colours with the value specified.
    lx, ly = image.size
    pixel = image.load()
    for y in range(ly):
        for x in range(lx):
            if pixel[x, y] == (0, 0, 0, 0):
                continue
            pixel[x, y] = image_colour

    # Put a mask of the original image over the colour-changed one.
    image.putalpha(mask)

    # Save the image to a buffer.
    colour_image = BytesIO()
    image.save(colour_image, "png")

    # Close images.
    image.close()
    mask.close()

    # Return image
    colour_image.seek(0)
    return colour_image

def do_pie_chart(values, names):

    labels = []
    percentages = []

    # Get the total sum of all the values.
    total = sum(values)
    # Calculate the percentage each value is out of the total.
    for value in values:
        value = round(value / total * 100, 2)
        percentages.append(value)

    # Append each percentage and its name to the labels.
    for name, percentage in zip(names, percentages):
        labels.append(f'{name}: {percentage}%')

    # Create a figure.
    figure = plt.figure(1, figsize=(4,3))

    # Create a subplot, with equal axis.
    axes = figure.add_subplot(111)
    axes.axis('equal')
    # Create the pir chart on the subplot.
    pie = axes.pie(values)

    # Set the positon of the axis to the left of the firgure.
    box = axes.get_position()
    axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Create a legend, which outside the area of the axis.
    axes.legend(pie[0], labels, loc="center left", fontsize=6, fancybox=True, bbox_to_anchor=(1, 0.5))

    # Save the image to a buffer.
    pie_chart = BytesIO()
    plt.savefig(pie_chart, bbox_inches="tight", transparent=True)

    # Close the image.
    plt.close()

    # Return image
    pie_chart.seek(0)
    return pie_chart

def do_bar_chart(title, x_label, y_label, values, names):

    # Clear the plot.
    plt.clf()

    #Create a bar graph with grid lines
    plt.bar(names, values, width=0.5, zorder=3)
    plt.grid(zorder=0)

    # Add labels
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)

    # Rotate x-labels by 90 degrees
    plt.xticks(rotation=-90)

    # Make the layout of plot conform to the text
    plt.tight_layout()

    # Save the image to a buffer.
    bar_chart = BytesIO()
    plt.savefig(bar_chart)

    # Close the image.
    plt.close()

    # Return image
    bar_chart.seek(0)
    return bar_chart

def do_plot(title, x_label, y_label, values, names):

    # Clear the current figure
    plt.clf()

    # Create a plot and add grid lines.
    plt.plot(names, values, "-r", zorder=3)
    plt.grid(zorder=0)

    # Add text labels
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)

    # Rotate x-labels by 90 degrees
    plt.xticks(rotation=-90)

    # Make the layout of plot conform to the text
    plt.tight_layout()

    # Save the image to a buffer.
    plot = BytesIO()
    plt.savefig(plot)

    # Close the image.
    plt.close()

    # Return image
    plot.seek(0)
    return plot


