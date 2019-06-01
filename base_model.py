#! /usr/bin/env python3
# *.* coding=utf-8
from PIL import Image
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract
import os
import requests


class base_model(object):
    def __init__(self):
        pass

    def get_random_string(self, length, num_number=0, capital_letters_list=0, lower_letters_numbers=0):
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

    def generate_pic_with_text(self, text):
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
        # 用这两个坐标之间的正方形区域生成一个圆, 大括号里的第二个参数为圆的开始角度
        # 第三个参数为圆的结束角度,0到360表示所画的是一个完整的圆形,
        # 也可以指定的数字来生成一段为圆弧,最后一个参数表示颜色,也可以用RGB来表示想要的颜色
        # draw.arc((100, 100, 300, 300), 0, 360, fill="red")
        draw.arc((0, 0, 300, 300), 0, 90, fill="blue")
        # 使用画笔的text方法在图片上生成文本
        # 第一个参数为坐标,第二个参数为所有生成的文本的内容
        # 第三个参数为文本的颜色

        myfont = ImageFont.truetype(
            "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", size=100)
        draw.text([0, 0], text, "blue", myfont)
        # gene_line('captcha.png')
        img.save('captcha.png', dpi=(127.0, 127.0))
        img.show()
        return 'captcha.png'

    def gen_captcha_from_url(url, num, folder):
        # https://login.anjuke.com/general/captcha?timestamp=15580192349965467 安居客

        if not os.path.exists(folder):
            os.mkdir(folder)
        pic = []
        for i in range(0, num):

            response = requests.get(url)
            filename = folder+'/' + str(i) + '.jpg'
            pic.append(filename)
            with open(filename, 'wb')as f:
                f.write(response.content)

        return pic

    def two_value(pic):
        img = Image.open(pic)
        # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
        Img = img.convert('L')
        # 模式  1   表示黑白图像，只有黑白

        Img.save(pic)
        # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
        threshold = 200

        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        # 图片二值化
        img = Img.point(table, '1')
        img.show()
        img.save(pic)

    def show_0_1_distribute(picname):
        img = Image.open(picname)
        img = img.convert('1')  # 返回一个Image对象

        width, height = img.size
        width /= 2
        height /= 2
        img = img.resize((int(width), int(height)), Image.ANTIALIAS)
        """
        point_list = []
        print('宽：%d,高：%d' % (im.size[0], im.size[1]))
        for y in range(0, im.size[1]):
            for x in range(0, im.size[0]):
                point = im.getpixel((x, y))
                point = 1 if point > 128 else 0
                print(point, end='')
            print('')
        """
        all_line = []
        for y in range(0, img.size[1]):
            line = ''
            for x in range(0, img.size[0]):
                point = img.getpixel((x, y))
                if point != 0:
                    point = 1
                line += str(point)
                # print(line)
            all_line.append(line+'\n')
        with open('res.html', 'w') as f:
            f.writelines(all_line)

    def de_noise(picname, de_num, limit_in_one_loop):
        # 总共循环进行de_num次对全图的去噪点 (从内圈开始,最外围的像素点直接去掉)
        # 当某像素点周围一圈的黑色像素点小于black_limit认为这是噪点，进行删除
        # 当某像素点周围两圈的黑色像素点小于limit_in_two_loop认为这是噪点，进行删除,默认不开启两圈去噪
        img = Image.open(picname)
        img = img.convert('1')
        # width, height = img.size
        # width /= 2
        # height /= 2
        # img = img.resize((int(width), int(height)), Image.ANTIALIAS)
        last_black = 0
        width, height = img.size
        for i in range(0, de_num):
            all_black = 0
            for x in range(1, img.size[0]-1):
                for y in range(1, img.size[1]-1):
                    value = img.getpixel((x, y))
                    point_list = [(x-1, y-1), (x-1, y), (x-1, y+1), (x, y - 1),
                                  (x, y + 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
                    # 这里我添加了对白点的去噪,当一个白点周围少于2个白点，将此白点设黑
                    if value != 0:
                        # 注意注意   虽然是以黑白模式打开，但实际上像素点的值还是原来的值,不一定为1
                        # continue
                        white_point_num = 0
                        for point in point_list:
                            if img.getpixel(point) != 0:
                                white_point_num += 1
                        if white_point_num < 3:
                            img.putpixel((x, y), 0)

                    else:
                        # 接下来是对黑点的去噪音
                        all_black += 1
                        black_point_num = 0
                        for point in point_list:
                            if img.getpixel(point) == 0:
                                black_point_num += 1
                        if black_point_num < limit_in_one_loop:
                            img.putpixel((x, y), 1)

            img.save(picname)
            print('all_black={}'.format(all_black))
            if last_black != all_black:
                last_black = all_black
            else:
                # 去噪到最后已经无点可去了,直接退出
                break
                # cmd = input('continue de_noise? (yes/no)：')
                # if cmd == 'yes':
                #    show_0_1_distribute(picname)
                #    img.show()
                # else:
                #    return
        show_0_1_distribute(picname)
        img.show()

    def check_right(self, folder):
        pic_list = os.listdir(folder)
        print(pic_list)
        right = 0
        all_pic = 0
        for pic in pic_list:
            if not '.tiff' in pic:
                continue
            all_pic += 1
            real = pic[:4]
            filename = 'code_pic/' + pic
            im = Image.open(filename)
            filename = filename.replace('.jpg', '.tiff')
            im.save(filename)  # or 'test.tif'
            result = pytesseract.image_to_string(
                filename, lang='normal', config='--psm 7 --oem 3 -c tessedit_char_whitelist=qwertyuiopasdfghjklzxcvbnm')
            print(filename + '=' + result, end='')

            if real == result:
                print('    yes', end='')
                right += 1
            print('\n')
        print('成功率：{right}/{all}={last}'.format(right=right,
                                                all=all_pic, last=float(right/all_pic)))
