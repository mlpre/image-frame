import os
import sys
import time
from datetime import datetime

import exifread
from PIL import ImageDraw, ImageFont, Image, ImageOps


def get_image_width(draw, text, font_size):
    font = ImageFont.load_default(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def get_image_height(draw, text, font_size):
    font = ImageFont.load_default(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def image_add_border(image_path, new_image_path, brand, model, lens, date_time, focal, f, iso, exposure):
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)
    width, height = image.size
    if width < 2000 or height < 2000:
        return
    dpi = image.info.get('dpi', (999, 999))
    if width > height:
        border_height = int(height / 10)
    else:
        border_height = int(width / 10)
    font_size = int(border_height / 5)
    font = ImageFont.load_default(font_size)
    padding = int(font_size / 2)
    new_height = height + border_height
    new_image = Image.new("RGB", (width, new_height), "white")
    new_image.paste(image, (0, 0))
    draw = ImageDraw.Draw(new_image)
    draw.text((int(width / padding), height + (border_height / 2)),
              brand, fill="black", font=font)
    draw.text((int(width / padding), height + (border_height / 4)),
              model, fill="black", font=font)
    draw.text((int(width / 2) - get_image_width(draw, date_time, font_size) / 2, height + (border_height / 2)),
              date_time, fill="black", font=font)
    draw.text((int(width / 2) - get_image_width(draw, lens, font_size) / 2, height + (border_height / 4)),
              lens, fill="black", font=font)
    data1 = focal + '  ' + f
    data2 = iso + '  ' + exposure
    draw.text(
        (int(width * (padding - 1) / padding) - get_image_width(draw, data1, font_size), height + (border_height / 4)),
        data1, fill="black", font=font)
    draw.text(
        (int(width * (padding - 1) / padding) - get_image_width(draw, data2, font_size), height + (border_height / 2)),
        data2, fill="black", font=font)
    new_image.save(new_image_path, dpi=dpi, quality=100)


def deal_image(image_path, new_image_path):
    with open(image_path, "rb") as file:
        tags = exifread.process_file(file)
        brand = str(tags.get('Image Make'))
        model = str(tags.get('Image Model'))
        lens = str(tags.get('EXIF LensModel'))
        date_time = str(tags.get('Image DateTime'))
        focal = str(tags.get('EXIF FocalLength'))
        f = str(tags.get('EXIF FNumber'))
        if '/' in f:
            numerator, denominator = map(int, f.split('/'))
            f = str(round(numerator / denominator, 1))
        iso = str(tags.get('EXIF ISOSpeedRatings'))
        exposure = str(tags.get('EXIF ExposureTime'))
        if brand == 'None':
            brand = ''
        if model == 'None':
            model = ''
        if lens == 'None':
            lens = ''
        if date_time == 'None':
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_time = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
        if focal == 'None':
            focal = ''
        else:
            focal = focal + 'mm'
        if f == 'None':
            f = ''
        else:
            f = 'F/' + f
        if iso == 'None':
            iso = ''
        else:
            iso = 'ISO' + iso
        if exposure == 'None':
            exposure = ''
        image_add_border(image_path, new_image_path, brand, model, lens, date_time, focal, f, iso, exposure)


if __name__ == '__main__':
    Image.MAX_IMAGE_PIXELS = None
    if hasattr(sys, "frozen"):
        directory = os.path.dirname(sys.executable)
    else:
        directory = os.path.dirname(__file__)
    filenames = os.listdir(directory)
    output_dir = os.path.join(directory, 'IMG' + str(int(time.time())))
    for filename in os.listdir(directory):
        if filename.lower().endswith('.jpg'):
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            deal_image(os.path.join(directory, filename), os.path.join(output_dir, filename))
