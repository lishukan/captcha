#! /usr/bin/env python
# *.* coding=utf-8
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract
import os
import requests


def gene_line(img):
    img = Image.open(img)
    width, height = img.size
    draw = ImageDraw.Draw(img, mode="RGB")
    begin = (random.randint(0, width), random.randint(0, height))
    end = (random.randint(0, width), random.randint(0, height))
    draw.line([begin, end], fill='black')

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强
    return img


def get_random_string(length, num_number=0, capital_letters_list=0, lower_letters_numbers=0):
    # param : 验证码长度，数字个数，大写字母个数，小写字母个数
    captcha_list = []
    # 参数合法
    if num_number + lower_letters_numbers + capital_letters_list == length:
        for i in range(0, num_number):
            captcha_list.append(random.choice(range(48, 57)))
        for i in range(0, lower_letters_numbers):
            captcha_list.append(random.choice(range(65, 91)))
        for i in range(0, capital_letters_list):
            captcha_list.append(random.choice(range(97, 122)))
    else:
        # 参数不合法则不根据大小写以及数字规定随机生成字符
        str_ascii_list = []
        for i in range(48, 58):
            str_ascii_list.append(i)
        for i in range(95, 123):
            str_ascii_list.append(i)
        for i in range(0, length):
            single_char = random.choice(str_ascii_list)
            captcha_list.append(single_char)
    # 上面得到的只是数字（ascii码）
    # 下面将数字转变成ascii字符
    for i in range(0, length):
        captcha_list[i] = chr(captcha_list[i])
    # 将字符串打乱顺序随机排列
    random.shuffle(captcha_list)  # 这个函数返回值为None，但直接调用即可
    return ''.join(captcha_list)


def generate_pic_with_text(text):
    img = Image.new(mode="RGB", size=(280, 140), color=(255, 255, 255))
    with open("captcha.png", "wb") as f:
        img.save(f, format="png")
    # 显示图片
    draw = ImageDraw.Draw(img, mode="RGB")
    # 在(100,100)坐标上生成一个红点,指定的坐标不能超过图片的尺寸
    # draw.point([100, 100], fill="red")
    # 在(80,80)坐标上生成一个黑点,指定的坐标不能超过图片的尺寸
    draw.point([80, 80], fill=(0, 0, 0))
    # for i in range(0, 10000):
    #    # 随机生成一万个点（噪点）
    #    x = random.choice(range(0, 280))
    #    y = random.choice(range(0, 140))
    #    draw.point([x, y], fill=(0, 0, 0))
    # 第一个括号里面的参数是坐标,前两个数为开始坐标,后两个数为结束坐标
    # 括号里的第二个参数指定颜色,可以直接指定,也可以用RGB来表示颜色
    draw.line((100, 100, 100, 300), fill="blue")
    draw.line((100, 200, 200, 100), fill="blue")
    # 括号里的第一个参数是坐标,前两个数为起始坐标,后两个为结束坐标
    #用这两个坐标之间的正方形区域生成一个圆, 大括号里的第二个参数为圆的开始角度
    # 第三个参数为圆的结束角度,0到360表示所画的是一个完整的圆形,
    # 也可以指定的数字来生成一段为圆弧,最后一个参数表示颜色,也可以用RGB来表示想要的颜色
    #draw.arc((100, 100, 300, 300), 0, 360, fill="red")
    draw.arc((0, 0, 300, 300), 0, 90, fill="blue")
    # 使用画笔的text方法在图片上生成文本
    # 第一个参数为坐标,第二个参数为所有生成的文本的内容
    # 第三个参数为文本的颜色

    myfont = ImageFont.truetype(
        "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", size=100)
    draw.text([0, 0], text, "blue", myfont)
    gene_line('captcha.png')
    img.save('captcha.png', dpi=(127.0, 127.0))
    img.show()
    return 'captcha.png'


def gen_captcha_from_url(num):
    # https://login.anjuke.com/general/captcha?timestamp=15580192349965467 安居客

    # if not os._exists('code_pic/'):
    #    os.mkdir('code_pic/')
    for i in range(0, num):
        fake_timestamp = get_random_string(8, 8, 0, 0)
        url = 'https://login.anjuke.com/general/captcha?timestamp='+fake_timestamp
        response = requests.get(url)
        filename = 'code_pic/'+str(i)+'.jpg'
        with open(filename, 'wb')as f:
            f.write(response.content)


if __name__ == "__main__":
    text = get_random_string(4, 1, 2, 1)
    #img = generate_pic_with_text(text)
    # print(text)
    # print(pytesseract.image_to_string('captcha.png'))
    gen_captcha_from_url(100)
