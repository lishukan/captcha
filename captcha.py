#! /usr/bin/env python
# *.* coding=utf-8
from PIL import Image
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract
import os
import requests
from base_model import base_model


if __name__ == "__main__":
    # 1. 从链接内拿到验证码
    url = 'https://xin.baidu.com/check/getCapImg?t=1559032504315'
    print(url)
    response = requests.get(url)
    print(response)
    base_model.gen_captcha_from_url(url=url, num=900, folder='xinbaidu_pic')
