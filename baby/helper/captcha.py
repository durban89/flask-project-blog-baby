# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-14 14:14:21
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-22 17:56:11
import random
from flask import session
from six import u
from PIL import Image, ImageFont, ImageDraw, ImageFilter

DISTANCE_FROM_TOP = 4


class Captcha(object):
    font_size = 12
    color_bg = '#007bff'
    color_fg = '#ffffff'
    punctuation = """_"',.;:-"""
    captch_length = 4
    rotation = (-35, 35)

    def __init__(self, font_path, scale=1, image_size=[100, 40]):
        self.image_size = image_size
        self.font_path = font_path
        self.scale = scale

    def get_size(self, font, text):
        if hasattr(font, "getoffset"):
            return tuple([x + y for x, y in zip(font.getsize(text),
                                                font.getoffset(text))])
        else:
            return font.getsize(text)

    def get_image_size(self, font, text):
        if self.image_size:
            size = self.image_size
        else:
            size = self.get_size(font, text)
            size = (size[0] * 2, int(size[1] * 1.4))

        return size

    def get_font(self):
        '''
        记载字体的时候需要知道文件的类型如果文件是ttf的话是不能直接使用
        ImageFont.load方法的

        不然会报 ‘cannot find glyph data file’
        '''
        if self.font_path.lower().strip().endswith('ttf'):
            font = ImageFont.truetype(
                self.font_path, self.font_size * self.scale)
        else:
            font = ImageFont.load(self.font_path)

        return font

    def make_image(self, image_size):
        if self.color_bg and \
                self.color_bg != 'transparent':
            image = Image.new('RGB', image_size, self.color_bg)
        else:
            image = Image.new('RGBA', image_size)
        return image

    def make_crop(self, image, size, xpos, char_image):
        if self.image_size:
            tmp_image = self.make_image(size)
            tmp_image.paste(
                image,
                (
                    int((size[0] - xpos) / 2),
                    int((size[1] - char_image.size[1]) / 2 - DISTANCE_FROM_TOP)
                )
            )
            image = tmp_image.crop((0, 0, size[0], size[1]))
        else:
            image = image.crop((0, 0, xpos + 1, size[1]))

        return tmp_image

    def get_text(self):
        chars, ret = u("abcdefghijklmnopqrstuvwxyz"), u("")
        for i in range(self.captch_length):
            ret += random.choice(chars)

        return ret.upper(), ret

    def get_char_list(self, text):
        charlist = []
        for char in text:
            if char in self.punctuation and len(charlist) >= 1:
                charlist[-1] += char
            else:
                charlist.append(char)

        return charlist

    def noise_image(self, draw, image):
        size = image.size

        draw.arc([
            -20,
            -20,
            size[0],
            20
        ], 0, 295, fill=self.color_fg)

        draw.line([
            -20,
            20,
            size[0] + 20,
            size[1] - 20
        ], fill=self.color_fg)

        draw.line([
            -20,
            0,
            size[0] + 20,
            size[1]
        ], fill=self.color_fg)

        for p in range(int(size[0] * size[1] * 0.1)):
            draw.point(
                (
                    random.randint(0, size[0]),
                    random.randint(0, size[1])
                ),
                fill=self.color_fg,
            )

        image.filter(ImageFilter.SMOOTH)

        return image

    @staticmethod
    def captcha_validate(text):
        captcha_val = session['captcha_key'] if \
            'captcha_key' in session else ''

        if captcha_val != text.lower():
            return False
        else:
            session.pop('captcha_key', None)

        return True

    def captcha(self):
        text, response = self.get_text()
        session['captcha_key'] = response

        font = self.get_font()
        image_size = self.get_image_size(font, text)
        image = self.make_image(image_size)

        char_list = self.get_char_list(text)

        xpos = 2

        for char in char_list:
            fgimage = Image.new("RGB", image_size, self.color_fg)
            char_image = Image.new('L', self.get_size(
                font, ' %s ' % char), '#000000')
            ImageDraw.Draw(char_image).text(
                (0, 0),
                ' %s ' % char,
                font=font,
                fill='#ffffff'
            )
            if self.rotation:
                char_image = char_image.rotate(
                    random.randrange(*self.rotation),
                    expand=0,
                    resample=Image.BICUBIC
                )
            char_image = char_image.crop(char_image.getbbox())
            mask_image = Image.new('L', image_size)

            mask_image.paste(
                char_image,
                (
                    xpos,
                    DISTANCE_FROM_TOP,
                    xpos + char_image.size[0],
                    DISTANCE_FROM_TOP + char_image.size[1]
                )
            )

            size = mask_image.size
            image = Image.composite(fgimage, image, mask_image)

            xpos = xpos + 2 + char_image.size[0]

        image = self.make_crop(image, size, xpos, char_image)

        draw = ImageDraw.Draw(image)

        image = self.noise_image(draw, image)

        return image
