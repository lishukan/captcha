#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
import traceback
import time, re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import requests
from io import BytesIO
import cv2 as cv
import time

def get_pos(image):
    blurred = cv.GaussianBlur(image, (3, 3), 0)
    canny = cv.Canny(blurred, 200, 400)
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        M = cv.moments(contour)
        if M['m00'] == 0:
            cx = cy = 0
        else:
            cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
        if 40 < cv.contourArea(contour)    :
            #if cx < 400:
            #    continue
            x, y, w, h = cv.boundingRect(contour)  # 外接矩形
            if 40 < w < 60 and 40 < h < 60:
                print('找到了，横坐标为', x)
            else:
                continue
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.imshow('image', image)
            print(cv.contourArea(contour),x)
            time.sleep(2)
            #return x
    return 0




def two_value(pic):
        new_pic='test'+pic
        img = Image.open(pic)
        # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
        width, height = img.size
        print(width,height)
        img = img.resize((int(width/2), int(height/2)), Image.ANTIALIAS)
        Img = img.convert('L')
        # 模式  1   表示黑白图像，只有黑白

        Img.save(new_pic)
        # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
        threshold =50

        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        # 图片二值化
        img = Img.point(table, '1')
        img.show()
        img.save(new_pic)

def show_0_1_distribute(picname):
    img = Image.open(picname)
    img = img.convert('L')  # 返回一个Image对象

    width, height = img.size
    print(img.size )
    width /= 2
    height /= 2
    #img = img.resize((int(width), int(height)), Image.ANTIALIAS)
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
    print(img.size  )
    all_line = []
    for y in range(0, img.size[1]):
        line = ''
        for x in range(0, img.size[0]):
            point = img.getpixel((x, y))
            #for i in len(0, 3):
            #    if point[i]
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

def is_sim(image1, image2, x, y):
    """
    对比两张图片RGB的值
    :param image1:
    :param image2:
    :param x:
    :param y:
    :return:
    """
    pixel1 = image1.getpixel((x,y))
    pixel2 = image2.getpixel((x,y))

    for i in range(0, 3):
        if abs(pixel1[i] - pixel2[i]) >= 50:
            return False
        return True

def get_diff_location(image1, image2):
    """
    计算缺口的位置 x坐标
    :param image1:
    :param image2:
    :return:
    """
    image1.save('1,jpg')
    image2.save('2,jpg')
    for x in range(0,260):
        for y in range(0, 116):
            if is_sim(image1, image2, x, y ) == False:
                return x


def get_track(distance):
    """
    模拟正常用户的滑动轨迹
    匀加速
    :param distance:
    :return:
    """
    #初速度
    v = 0
    #单位时间 秒
    t = 0.2
    #当前移动的x的坐标
    current = 0

    #位移的轨迹
    tracks = []
    distance += 10

    #阀值
    mid = distance * 7/8

    while current < distance:
        if current < mid:
            #加速度
            a = random.randint(2, 4)
        else:
            a = random.randint(3, 5)
        v0 = v
        #单位时间的位移
        s = v0 * t + 0.5*a * (t ** 2)
        current += s
        v = v0 + a*t
        tracks.append(round(s))
    for i in range(3):
        tracks.append(-random.randint(1, 3))
    for i in range(3):
        tracks.append(-random.randint(2, 3))

    return tracks






def get_page(url):
    my_options=webdriver.FirefoxOptions()
    #my_options.add_argument('--headless')
    my_options.add_argument('--disable-gpu')
    driver=webdriver.Firefox(options=my_options)
    #driver.set_window_size(1125,1880)
    driver.get(url)
    time.sleep(2)
    res=driver.page_source
    #driver.quit()

    #ele=driver.find_element_by_css_selector('body > div.account-body.login-wrap.login-start.account-anonymous > div.account-body-tabs > ul.tab-start > li.account-tab-account')
    #ele=driver.find_element_by_xpath('/html/body/div[1]/div[1]/ul[1]/li[2]')
    frame=driver.find_element_by_xpath('//*[@id="anony-reg-new"]/div/div[1]/iframe')
    driver.switch_to_frame(frame)
    ele = driver.find_element_by_class_name('account-tab-account')
    ele.click()
    driver.find_element_by_id('username').send_keys('13755235326')
    driver.find_element_by_id('password').send_keys('13755235326')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[5]/a').click()
    
    while True:
        time.sleep(1)
        try:
            
            frame = driver.find_element_by_xpath('//*[@id="TCaptcha"]/iframe')
            driver.switch_to_frame(frame)
            print('切换到frame')
            ele = driver.find_element_by_xpath('//*[@id="tcaptcha_drag_button"]')
            print('找到了 拖动框')
            ActionChains(driver).move_to_element(ele)
            ActionChains(driver).click_and_hold(on_element=ele).perform()
            time.sleep(0.5)
            distance=500
            while distance > 0:
                if distance > 10:
                    # 如果距离大于10，就让他移动快一点
                    span = random.randint(5, 8)
                else:
                    # 快到缺口了，就移动慢一点
                    span = random.randint(2, 3)
                ActionChains(driver).move_by_offset(span, 0).perform()
                distance -= span
                time.sleep(random.randint(10, 50) / 100)

            ActionChains(driver).move_by_offset(distance, 1).perform()
            ActionChains(driver).release(on_element=ele).perform()
        except NoSuchElementException:
            print('error')
            driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[5]/a').click()
            pass
        except:
            traceback.print_exc()
            driver.quit()
            return 
        
    
    time.sleep(5)
    #driver.switch_to_default_content()
    






if __name__ == "__main__":
    url='https://www.douban.com/'
    get_page(url)
    pic='slide.jpeg'
    #two_value(pic)
    show_0_1_distribute(pic)