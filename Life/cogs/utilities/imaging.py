from PIL import ImageDraw, ImageFilter, Image
from io import BytesIO


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


def colour(image_bytes, fg_colour, bg_colour):
    # Open the image_bytes as an image and covert it to black and white.
    bw_image = Image.open(BytesIO(image_bytes)).convert('L')
    # Smooth the image.
    bw_image = bw_image.filter(ImageFilter.SMOOTH)
    # Get the size of the image.
    lx, ly = bw_image.size
    # Create a new image to add our pixels too.
    colour_image = Image.new('RGB', (lx, ly))
    # Loop through all pixels and decide whether to the give them bg_colour or fg_colour based on thier own colour.
    for x in range(lx):
        for y in range(ly):
            v = bw_image.getpixel((x, y))
            if v > 120:
                colour_image.putpixel((x, y), fg_colour)
            else:
                colour_image.putpixel((x, y), bg_colour)
    # Smooth the new image
    colour_image = colour_image.filter(ImageFilter.SMOOTH)

    # Save the image to a buffer.
    image = BytesIO()
    colour_image.save(image, "png")

    # Close images.
    bw_image.close()
    colour_image.close()

    # Return image
    image.seek(0)
    return image


def gif(image_bytes):

    frames = []

    x, y = 0, 0

    avatar_img = Image.open(BytesIO(image_bytes)).copy()

    for i in range(512):

        gif_image = Image.new('RGB', (512, 512), (255, 255, 255))
        gif_image.paste(avatar_img, (x, y))

        frames.append(gif_image)
        frames.append(gif_image)

        x += 1
        y += 1

    # Save the image to a buffer.
    image = BytesIO()
    frames[0].save(image, save_all=True, format='gif', append_images=frames, loop=0)

    avatar_img.close()
    for frame in frames:
        frame.close()

    # Return image
    image.seek(0)
    return image


