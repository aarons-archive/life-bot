from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from PIL import Image
import discord


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


def do_imageinfo(data, member, avatar_bytes):

    # Define the fonts.
    font = ImageFont.truetype("files//fonts/OpenSans-Regular.ttf", 40)
    bigfont = ImageFont.truetype("files//fonts/OpenSans-Regular.ttf", 50)

    # Get the users backround based on their choice.
    background_img = Image.open(f"files/images/backgrounds/{data['background']}.png")

    # Open the users avatar, resize, and then round it.
    avatar_img = Image.open(BytesIO(avatar_bytes))
    avatar_img = avatar_img.resize([250, 250])
    avatar_img = round_image(avatar_img, 50)

    # Copy rounded avatar to background image.
    avatar_img = avatar_img.copy()
    background_img.paste(avatar_img, (700, 50), avatar_img)

    # Allow for drawing on the background image.
    background_draw = ImageDraw.Draw(background_img)

    # Add text to background image.
    background_draw.text((50, 35), f"{member}", (255, 255, 255), align="center", font=bigfont)
    if member.nick is not None:
        background_draw.text((50, 90), f"{member.nick}", (255, 255, 255), align="center", font=font)

    # Add status circles to the backround image based on the users status.
    if member.status == discord.Status.online:
        background_draw.ellipse((915, 265, 965, 315), fill=(0, 128, 0, 0))
    if member.status == discord.Status.idle:
        background_draw.ellipse((915, 265, 965, 315), fill=(255, 165, 0, 0))
    if member.status == discord.Status.dnd:
        background_draw.ellipse((915, 265, 965, 315), fill=(255, 0, 0, 0))
    if member.status == discord.Status.offline:
        background_draw.ellipse((915, 265, 965, 315), fill=(128, 128, 128, 0))

    # Round the backround image and resize it.
    background_img = round_image(background_img, 100)

    # Save the image into a bytesio stream
    imginfo = BytesIO()
    background_img.save(imginfo, "png")

    # Close images.
    background_img.close()
    avatar_img.close()

    # Return image
    imginfo.seek(0)
    return imginfo
