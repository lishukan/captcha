#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import numpy as np
import traceback
import time, re
import sys,os.path
abspath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(".."))
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException,NoSuchElementException,ElementClickInterceptedException,ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import requests
from io import BytesIO
import cv2 as cv
import os
from PIL import Image
from base.base_model import BaseModel

def debug(func,switch=False):
    def wrapper(*args, **kwargs):  # 指定宇宙无敌参数
        if switch==True:
            print("[DEBUG]: enter {}(), time={},".format(func.__name__,time.time()))
        #print ('Prepare and say...',)
        return func(*args, **kwargs)
    return wrapper  # 返回


@debug
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
    #img.show()
    for i in range(0, de_num):
        all_black = 0
        for x in range(1, img.size[0] - 1):
            for y in range(1, img.size[1] - 1):
                if x < 52:  #统统将x
                    img.putpixel((x, y), 1)
                    continue
                value = img.getpixel((x, y))
                point_list = [(x-1, y-1), (x-1, y), (x-1, y+1), (x, y - 1),
                                (x, y + 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
                # 这里我添加了对白点的去噪,当一个白点周围少于3个白点，将此白点设黑
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
        #print('all_black={}'.format(all_black))
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

    #img.show()
    #time.sleep(2)
    return picname


def two_value(pic):
    new_pic='test'+pic
    img = Image.open(pic)
    # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
    width, height = img.size
    #print(width,height)
    #img = img.resize((int(width/2), int(height/2)), Image.ANTIALIAS)
    Img = img.convert('L')
    # 模式  1   表示黑白图像，只有黑白
    #Img.show()
    Img.save(new_pic)
    # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
    threshold =90

    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    # 图片二值化
    img = Img.point(table, '1')
    #img.show()
    img.save(new_pic)
    return new_pic

"""
RETR_EXTERNAL：只检测最外围轮廓，包含在外围轮廓内的内围轮廓被忽略；

RETR_LIST：检测所有的轮廓，包括内围、外围轮廓，但是检测到的轮廓不建立等级关系，彼此之间独立，没有等级关系，这就意味着这个检索模式下不存在父轮廓或内嵌轮廓，所以hierarchy向量内所有元素的第3、第4个分量都会被置为-1，具体下文会讲到；

RETR_CCOMP: 检测所有的轮廓，但所有轮廓只建立两个等级关系，外围为顶层，若外围内的内围轮廓还包含了其他的轮廓信息，则内围内的所有轮廓均归属于顶层；

RETR_TREE: 检测所有轮廓，所有轮廓建立一个等级树结构。外层轮廓包含内层轮廓，内层轮廓还可以继续包含内嵌轮廓。

参数5：定义轮廓的近似方法，取值如下：

CHAIN_APPROX_NONE：保存物体边界上所有连续的轮廓点到contours向量内；

CHAIN_APPROX_SIMPLE：仅保存轮廓的拐点信息，把所有轮廓拐点处的点保存入contours向量内，拐点与拐点之间直线段上的信息点不予保留；

CHAIN_APPROX_TC89_L1：使用teh-Chinl chain 近似算法;

CHAIN_APPROX_TC89_KCOS：使用teh-Chinl chain 近似算法。
"""


def get_pos(image_name):
    """
    返回可能的选择列表，元素为元祖 （x，offset）  ，按照offset即（w+h）/2 离50最接近的顺序排序
    """
    print("正在对",image_name,"进行边缘检测")
    possible_position=[]
    #image_name=de_noise(image_name,3,3) #想想还是不人为降噪了。
    image = cv.imread(image_name)
    blurred = cv.GaussianBlur(image, (5, 5), 0)
    canny = cv.Canny(blurred, 200, 400)
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    x, y, w, h = 50, 0, 0, 0
    for i, contour in enumerate(contours):
        x, y, w, h = cv.boundingRect(contour)  # 外接矩形
        #print(x, '+++++++++++', cv.contourArea(contour))
        #print("w:",w,"h",h)
        M = cv.moments(contour)
        if M['m00'] == 0:
            cx = cy = 0
        else:
            cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
        #    print("cx==",cx,"cy==",cy)
        if 10< cv.contourArea(contour) :
            #if cx < 400:
            #    continue
            #print(cx,cy)
            x, y, w, h = cv.boundingRect(contour)  # 外接矩形
            if 20< w < 60 and 20 < h < 60 and x>52:
                #print('找到了，横坐标为', x)
                #print(cv.contourArea(contour), x)
                offset= abs(  int(50-(w+h)/2))
                possible_position.append(  (x,offset)   )
                cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            else:
                continue

            
    #cv.imshow('image', image)

    

    #cv.waitKey(10)

    #print("可能的选择是：",sorted( possible_position,key=lambda d:d[1],reverse = False))

    return sorted( possible_position,key=lambda d:d[1],reverse = False)




class Qgrzrk_model(BaseModel):
    
    def __init__(self, driver=None):
        if not driver:
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox') 
            options.add_argument('--disable-dev-shm-usage') 
            driver = webdriver.Chrome(options=options)
        self.driver=driver
        self.wait=WebDriverWait(self.driver,10)


    def __del__(self):
        try:
            if hasattr(self,'driver'):
                self.driver.quit()
        except ImportError:
            print("driver 未启动 ")

    


    def refresh_script(self):
        js1 = '''() =>{

           Object.defineProperties(navigator,{
             webdriver:{
               get: () => false
             }
           })
        }'''

        js2 = '''() => {
                alert (
                    window.navigator.webdriver
                )
            }'''

        js3 = '''() => {
                window.navigator.chrome = {
            runtime: {},
            // etc.
        };
            }'''

        js4 = '''() =>{
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
            });
                }'''

        js5 = '''() =>{
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5,6],
        });
                }'''
        self.driver.execute_script(js1)
        self.driver.execute_script(js2)
        self.driver.execute_script(js3) 
        self.driver.execute_script(js4)
        self.driver.execute_script(js5)

    
    def start(self):
        while True:
            company = self.redis_util.pop_from_set('need_cert_company_names')
            self.redis_util.insert2set('need_cert_company_names', company)
            print("开始搜索此公司",company)
            if self.search(company):
                print("此企业搜索到了结果",company)
                with open('已经搜索到信息的公司', 'a') as f:
                    f.write(company+'\n')
                
            else:
                print("此公司未搜索到结果：",company)
                with open('未搜索到认证信息的公司', 'a') as f:
                    f.write(company+'\n')
            self.redis_util.remove_from_set('need_cert_company_names',company) #程序全部走完才会在redis内删除此条记录

    def search(self, key_word):
        result_list=[]
        for i in range(0,3):
            url = 'http://cx.cnca.cn/CertECloud/result/skipResultList?certNumber=&orgName={}&fromIndex=true'.format(key_word)
            self.driver.get(url)
            self.driver.implicitly_wait(5)
            self.refresh_script()

            self.find_and_do_captcha()
            for orgName_num in range(1, 6):  #最多五个企业
                print("这是第",orgName_num,"家企业")
                for i in range(1, 4):  # 每个重试三次
                    print("第,",i,",次试试")
                    content = self.get_info(orgName_num )
                    if content:
                        result_list.append(self.parse_results(content))
                        break
                    elif content == False and  orgName_num>1:
                        return  result_list


                    #elif result == False:
                    #    self.find_and_do_captcha()           
            if not result_list:
                continue

        #cv.destroyAllWindows()
        return result_list


    @debug
    def parse_results(self, results):
        if not isinstance(results, list):
            results=[results,]   
        insert_result=[]
        for r in results:
            r = re.sub('[\r\t\n]', '', r)
            r = r.strip()
            with open('results.html', 'a') as f:
                f.write(str(r))
            #print(r)
            #print("难道是正则解析的时候卡主了？")
            data_list = re.findall('(\S*?)证书编号[\s:]+(\S+)\s+(\S*?)认证项目/产品类别[\s:]+(\S+)\s+.*?(20\d\d-\d+-\d+).?发证机构[\s:]+(\S+)', r)
            print(type( data_list))
            print(data_list)
            for company_name, certification_no, status,certification_name, expire_date, agency in data_list:
                #print("难道是这？")
                data = dict()
                data['company_name'] =company_name
                data['certification_no'] =certification_no
                data['certification_name']= certification_name
                data['status'] = status
                data['expire_date'] = expire_date
                data['agency'] = agency
                if "安全" in certification_name:_type = 1
                elif "质量" in certification_name:_type = 2
                elif "环" in certification_name:_type = 3
                else: _type = 0
                data['type']=_type
                insert_result.append(self.save2mysql(data))

        print("结束解析")
        if insert_result:
            return True

    
    @debug
    def find_and_do_captcha(self):
        """
        return   None 未发现验证码
        return   False 验证码校验失败
        return   True 验证码校对成功
        """
        #captcha_element=self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        button = self.get_geetest_button()
        if not button:
            print("不可能，怎么会一张验证码都没有")
        else:
            for i in range(1, 5):
                two_value_pic = self.get_two_value_captcha()
                if two_value_pic == None: #如果验证码不可见
                    if self.check_if_pass(): #而且检测出来验证码已经通过
                        return True
                else:
                    distance_list = get_pos(two_value_pic)  #得到可能的位置(可能 会返回好几个位置)
                    for distance,offset in distance_list:
                        tracks = self.get_tracks_2(distance,1.0)
                        print("try change distance to -->,",distance)
                        #print(tracks)
                        #tracks=[distance]
                        self.move_to_gap(tracks)
                        time.sleep(1)
                        if self.check_if_pass():
                            return  True
            
                self.refresh_captcha() #刷新验证码
            return False


    @debug
    def get_two_value_captcha(self):
        pic = self.get_geetest_image(name='captcha_pic.png')  #截验证码部分图片
        if pic == None: #有验证码但是没有可见的验证码
            return None
        os.rename('captcha_pic.png','captcha_pic.jpeg') #重命名为jpeg格式
        two_value_pic = two_value('captcha_pic.jpeg')  #二值化 
        print(two_value_pic)
        return  two_value_pic

    @debug
    def check_if_pass(self):
        """
        共有两种错误
        1. 验证码拉到位了，但是提示网络问题/拼图被怪物吃了 等
        2. 验证码没有拉到位   
        """

        print("尝试检测是否出现验证失败")         
        capt_pos = self.get_captcha_position()
        if capt_pos!=(0,0,0,0):
            print(capt_pos)
            print("验证码还在  ，验证码没有拉到位   ，需要重新滑动")
            return False
        ele = self.driver.find_elements_by_class_name('geetest_panel_error_content')
        if ele[-1].is_displayed():
        # ele[-1].click()
            print("提示网络问题/拼图被怪物吃了，立即点击重试")
            retry_js="refresh=document.getElementsByClassName('geetest_panel_error_content');refresh[refresh.length-1].click();"
            self.driver.execute_script( retry_js)
            return False
        else:
            print("验证通过")
            # os.remove('captcha_pic.jpeg')
            return True

    @debug
    def save2mysql(self, data):
        company_id=self.mysql_util.query('company',{'company_name':data['company_name']})
        if not company_id:
            print("此条数据的企业名不存在公司企业库，将被舍弃:", data['company_name'])
        data['company_id'] = company_id
        del data['company_name'] #表中没有这个字段，需要删掉
        condition={'company_id':company_id,'certification_no':data['certification_no']}
        already_exists_id=self.mysql_util.query('certification',condition=condition)
        if already_exists_id:
            print("此条数据已经在数据库中存在：id=", already_exists_id)
            return self.mysql_util.update('certification',data,already_exists_id)
        else:
            return self.mysql_util.insert('certification',data)



    @debug
    def refresh_captcha(self):
        print("刷新验证码")
        try:
            # ele = self.driver.find_elements_by_class_name("geetest_refresh_1")
            # ele[-1].click()
            refresh_js="refresh=document.getElementsByClassName('geetest_refresh_1');refresh[refresh.length-1].click();"
            self.driver.execute_script( refresh_js)
        except:
            traceback.print_exc()

        time.sleep(1)

    @debug
    def get_info(self,orgName_num):
        print("get info")


        try:
            self.find_and_do_captcha()
            ele = self.driver.find_element_by_id("orgName{}".format(orgName_num))

            if ele.is_displayed():
            # ele[-1].click()
                print("找到该企业了：",ele.text.strip())
                refresh_js="refresh=document.getElementById('orgName{}').click();".format(orgName_num)
                self.driver.execute_script(refresh_js)

            else:
                print("该企业不可见")
            self.find_and_do_captcha()
        except NoSuchElementException:
            print("未找到该企业:orgName{}".format(orgName_num))
            return False
            
        # except ElementClickInterceptedException:
        #     print("点击公司的时候出错，可能是被验证码挡住了")
        #     self.find_and_do_captcha()

        # except NoSuchElementException:
        #     print("没有搜索到企业")
        #     return None

        time.sleep(2)


        try:
            text = self.driver.find_element_by_class_name('certContent')
            print( dir(text))
            print(text.text)
            return text.text
        except NoSuchElementException:
            print('此企业未搜索到证书')
        except:
            traceback.print_exc()


        return None



    # def find_captcha(self,class_name='geetest_slider_button'):
    #     capt_pos = self.get_captcha_position()
    #     if capt_pos!=(0,0,0,0):
    #         print(capt_pos)
    #         print("验证码还在  ，验证码没有拉到位   ，需要重新滑动")
    #         return capt_pos
    #     else:
    #         return False



        
    @debug
    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return:
        """
        # 验证按钮
        for i in range(1,3):
            try:
                element =self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,"geetest_slider_button")))
                button = self.driver.find_elements_by_class_name("geetest_slider_button")
                return button[-1]
            except TimeoutException:
                continue
            
        return False

    @debug
    def get_captcha_element(self):
        """
        返回最新的验证码元素
        """
        try:
            img_list = self.driver.find_elements_by_class_name("geetest_canvas_img")
            print('找到了验证码图片')
            return img_list[-1]
        except:
            traceback.print_exc()
            print("未找到验证码图片的位置")
            return False

    @debug
    def get_captcha_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """

        img=self.get_captcha_element()
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    @debug
    def get_geetest_image(self, name):
        """
        获取验证码图片
        :return: 图片对象
        """
        time.sleep(2)
        top, bottom, left, right = self.get_captcha_position()
        if top == 0 and left == 0:
            return None
        print('验证码位置', top, bottom, left, right)
        time.sleep(1.5)

        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)

        return name
    # def delete_style(self):
    #     '''
    #     执行js脚本，获取无滑块图
    #     :return None
    #     '''
    #     js = 'document.querySelectorAll("canvas")[2].style=""'
    #     self.driver.execute_script(js)

    # def get_gap(self, image1, image2):
    #     """
    #     获取缺口偏移量
    #     :param image1: 带缺口图片
    #     :param image2: 不带缺口图片
    #     :return:
    #     """
    #     left = 50
    #     print(image1.size[0])
    #     print(image1.size[1])
    #     diff_count=0
    #     for i in range(left+25, image1.size[0]-10):
    #         for j in range(3,image1.size[1]-10):
    #             print('i={},j={}'.format(i,j))
    #             if self.is_different(image1, image2, i, j):
    #                 diff_count += 1
    #                 if diff_count > 4:
    #                     return i
    #             else:
    #                 diff_count=0

    #     return left

    # def is_different(self, image1, image2, x, y):
    #     """
    #     判断两个像素是否不同
    #     :param image1: 图片1
    #     :param image2: 图片2
    #     :param x: 位置x
    #     :param y: 位置y
    #     :return: 像素是否相同
    #     """
    #     # 取两个图片的像素点
    #     pixel1 = image1.load()[x, y]
    #     pixel2 = image2.load()[x, y]
    #     print(pixel1,pixel2)
    #     threshold = 80
    #     with open('diff.txt', 'a') as f:
    #         f.write( str(x)+'+'+str(y)+':'+str(pixel1)+str(pixel2)+'\n'   )
    #     if abs(pixel1[0] - pixel2[0]) > threshold and abs(pixel1[1] - pixel2[1]) >threshold  and abs(pixel1[2] - pixel2[2]) > threshold:
    #         return True
    #     else:
    #         return False


    @debug    
    def get_track(self, distance):
        '''
        根据偏移量获取以哦对那个轨迹
        先做匀加速运动  后匀减速运动
        :param distance:
        :return: 移动轨迹
        '''
        #滑块起始位置与图片边缘有点点距离差距 可做点调整
        distance-=2.4
        track = []

        current = 0
        mid = distance * 3 / 4
        t = 0.1
        v = 0
        move=5
        while current < distance:
            if current < mid:
                a = random.choice(range(4,7))
            else:
                a = random.choice(range(-4,-2))

            v0 = v
            v = v0 + a * t
            move = v0 * t + 1/2 * a * t * t
            current += round(move)

            #print('目前距离:', current)
            track.append(round(move))
        


        move = distance - sum(track)-1
        track.append(round(move))
        print("实际移动距离："+ str(sum(track)))
        return track


    def ease_out_quad(self, x):
        return 1 - (1 - x) * (1 - x)

    def ease_out_quart(self, x):
        return 1 - pow(1 - x, 4)

    def ease_out_expo(self, x):
        if x == 1:
            return 1
        else:
            return 1 - pow(2, -10 * x)


    def get_tracks_2(self, distance, seconds, ):
        """
        根据轨迹离散分布生成的数学 生成  # 参考文档  https://www.jianshu.com/p/3f968958af5a
        成功率很高 90% 往上
        :param distance: 缺口位置
        :param seconds:  时间
        :param ease_func: 生成函数
        :return: 轨迹数组
        """
        distance += 15
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            ease = self.ease_out_expo
            offset = round(ease(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
        print(tracks)
        return tracks



    @debug
    def move_to_gap(self, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        slider=self.get_geetest_button()
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.02)
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()


if __name__ == "__main__":
    renzheng_model = Qgrzrk_model()
    #renzheng_model.start()
    renzheng_model.search('浙江金豪环境建设有限公司')