from PIL import ImageDraw
from io import BytesIO
from PIL import Image


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
