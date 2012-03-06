# -*- coding: utf-8 -*-

"""
    image
   ~~~~~~

    画像処理に関するユティリティ。
"""


import PIL
from PIL import Image, ImageDraw


def triming(image_file, color=(255, 255, 255)):
    """画像の余白をトリミングする。

    * *image_file* 画像ファイルのパス
    * *color* 余白の背景色をRGB tuple形式で指定する
      デフォルトは白
    """

    img = Image.open(image_file)
    width, height = img.size

    if img.mode.lower() == 'rgba':
        color += (255, )

    w = 256
    h = int(height * w / width)
    thumb_size = w, h

    thumb = img.copy()
    thumb.thumbnail(thumb_size)
    pix = thumb.load()

    def get_cx():
        for x in range(1, w)[::-1]:
            for y in range(1, h)[::-1]:
                if pix[x, y] != color:
                    return x
    cx = get_cx() or 1

    def get_cy():
        for y in range(1, h)[::-1]:
            for x in range(1, w)[::-1]:
                if pix[x, y] != color:
                    return y
    cy = get_cy() or 1

    """
    box = thumb.crop((0, 0, cx, cy))
    box.save(image_file + 'thumb.png')
    """
    del thumb

    scale_w = cx * 1.0 / w
    scale_h = cy * 1.0 / h
    new_w = int(width * scale_w + 5 * width / w)
    new_h = int(height * scale_h + 5 * height / h)

    box = img.crop((0, 0, new_w, new_h))
    del img

    #return box
    box.save(image_file)
    del box


def add_frame(image_file, outline='#000'):
    """画像の周りにフレームを追加する。

    * *image_file* 画像ファイルのパス
    * *outline* 縁の色をRGB文字列形式で指定する
      デフォルトは黒
    """

    img = Image.open(image_file)
    w, h = img.size
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w-1, h-1), outline=outline)
    del draw
    img.save(image_file)
    del img

