from io import BytesIO

import matplotlib.pyplot as plt
from PIL import ImageDraw, Image


async def get_image(bot, url):
    async with bot.session.get(url) as response:
        image_bytes = await response.read()
    return image_bytes

def round_image(image, rad):
    circle = Image.new("L", (rad * 2, rad * 2))
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new("L", image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    image.putalpha(alpha)
    return image

def resize_image(image_bytes, height, width):
    image = Image.open(BytesIO(image_bytes))
    img_width, img_height = image.size
    if img_height == height and img_width == width:
        return image
    image = image.resize([height, width])
    return image

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
