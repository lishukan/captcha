#! /usr/bin/env python3
# *.* coding=utf-8
from PIL import Image
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract
import os
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException


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


def gen_captcha_from_url(url, num, folder):
    # https://login.anjuke.com/general/captcha?timestamp=15580192349965467 安居客

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=F42AA89C1C428FFC7320AB328C134747; SESSION=560f0373-77bb-430a-a560-a52efbf0a1e8; FSSBBIl1UgzbN7N80S=WPJOqa0Pdyw8y5R34rj5N_mRHWuo0fb.Bnj1qPKXm3JRmVkXVyXr89iXw1M8pREE; Hm_lvt_d59e2ad63d3a37c53453b996cb7f8d4e=1561782240; _gscu_15322769=61782269j06iqc13; _gscbrs_15322769=1; Hm_lpvt_d59e2ad63d3a37c53453b996cb7f8d4e=1561793050; FSSBBIl1UgzbN7N80T=3LH5Qr7I_dPXQH6c649nTfEMPjoO_sGcprZDWU8RuJdR8a4Qr_2w5IdSu8DQ9..AP4pgxvHMX_BDEN_8iwhy6jYOYRNUNpJNvkpyKOf6VTe2jzIHQrW3J1VQp.4bmNModLnuKQLm1Imrh4HSEte9jBKFFWmOqJ4dbm_.nwDtp7DmkJ3JQ9q936UdS7Ptaq19.gqk.X3dO6U6N2UKGWCVk6qFqRp_0PrknP7nHAfheNeoQbCFv.bYizAQ08Z41WmO6tnIZ4JcVtJSPE0hY1JGFh_Vuj0PluFp8h7VmEAuIvRKJmiP1PK0iOvn_ET2ooEYJ22EEndMzCEia1g6OfAbgFCVuzKxmoJ3d0upH2ENq1j2qkA",
        "Host": "zxgk.court.gov.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
    }
    if not os.path.exists(folder):
        os.mkdir(folder)
    pic = []
    for i in range(21, num):

        response = requests.get(url, headers=headers)
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
    # img.show()

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


def de_noise(picname, de_num=10, limit_in_one_loop=4):
    # 总共循环进行de_num次对全图的去噪点 (从内圈开始,最外围的像素点直接去掉)
    #
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
    # show_0_1_distribute(picname)
    # img.show()
    return img


def check_right(pic_list):

    right = 0
    all_pic = len(pic_list)
    for pic in pic_list:
        # if not '.tiff' in pic:
        #    continue
        all_pic += 1
        real = pic[:4]
        filename = pic
        im = Image.open(filename)
        #filename = filename.replace('.jpg', '.tiff')
        im.save(filename)  # or 'test.tif'
        result = pytesseract.image_to_string(
            filename, lang='eng', config='--psm 7 --oem 3')
        print(filename + '=' + result, end='')

        if real == result:
            print('  yes', end='')
            right += 1
        print('\n')
    print('成功率：{right}/{all}={last}'.format(right=right,
                                            all=all_pic, last=float(right/all_pic)))


def get_all_pic(folder):
    file_list = os.listdir(folder)
    all_pic = []
    for file in file_list:
        if 'jpeg' not in file and 'jpg' not in file:
            continue
        all_pic.append(folder+'/'+file)
    return all_pic


if __name__ == '__main__':
    all_pic = get_all_pic('原图')

    for pic in all_pic:
        two_value(pic)
        img = de_noise(pic)
        new_name = re.sub('(.*?/)', '二值化并且降噪后/', pic)
        img.save(new_name)
