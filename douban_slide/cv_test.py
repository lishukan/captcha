# encoding:utf-8
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


if __name__ == '__main__':
    img0 = cv.imread('testslide.jpeg')
    print(get_pos(img0))
    cv.waitKey(0)
    cv.destroyAllWindows()