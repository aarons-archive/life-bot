from io import BytesIO

from PIL import ImageDraw, Image, ImageSequence


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


def colour_gif(image_bytes, image_colour):

    # Open the image_bytes as an image and covert it to an RGBA type image.
    image = Image.open(BytesIO(image_bytes))

    # Define a list to store changed frames in.
    frames = []

    # Loop through the frames of the gif.
    for frame in ImageSequence.Iterator(image):

        # Convert the frame to RGBA format
        frame = frame.convert("RGBA")

        # Create a mask for the image with the alpha layer.
        mask = frame.convert("L")

        # Switch pixels colours with the value specified.
        lx, ly = frame.size
        pixel = frame.load()
        for y in range(ly):
            for x in range(lx):
                if pixel[x, y] == (0, 0, 0, 0):
                    continue
                pixel[x, y] = image_colour

        # Put a mask of the original image over the colour-changed one.
        frame.putalpha(mask)

        # Append the frame to the list of frames.
        frames.append(frame)

    # Save the image to a buffer.
    colour_image = BytesIO()
    frames[0].save(colour_image, save_all=True, format='gif', append_images=frames[1:], loop=0, transparency=100, disposal=2)

    # Close images.
    image.close()
    for frame in frames:
        frame.close()

    # Return image
    colour_image.seek(0)
    return colour_image
