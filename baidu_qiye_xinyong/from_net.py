# coding=utf-8
#from gen_captcha import gen_captcha_text_and_image
#from gen_captcha import number
#from gen_captcha import alphabet
#from gen_captcha import ALPHABET
import traceback
import os
import os.path
import random
import numpy as np
import tensorflow as tf
from PIL import Image
import re
number = []
alphabet = []

# 百度企业信用给的验证码里没有0，o   1和l 这种难分辨的字母
CHAR_SET = ['2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n',  'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
"""
text, image = gen_captcha_text_and_image()
print  "验证码图像channel:", image.shape  # (60, 160, 3)
# 图像大小
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160
MAX_CAPTCHA = len(text)
print   "验证码文本最长字符数", MAX_CAPTCHA  # 验证码最长4字符; 我全部固定为4,可以不固定. 如果验证码长度小于4，用'_'补齐
"""
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160
MAX_CAPTCHA = 4

# 把彩色图像转为灰度图像（色彩对识别验证码没有什么用）

PICS_DIR='xinbaidu_pic' #训练集
PICS_LIST= os.listdir(PICS_DIR)
print(PICS_LIST)


def get_single_image_and_text(image_name):

    image = Image.open(image_name)
    image = image.resize(
        (int(IMAGE_WIDTH), int(IMAGE_HEIGHT)), Image.ANTIALIAS)
    # captcha_image.show()
    image = np.array(image)

    text = re.findall('(.*?)\.jpg', image_name)[0]
    #pic = os.path.join(PICS_DIR,image_name)

    # print(text)
    #os.rename(pic,pic.replace(text,text.lower()))
    text = text.lower()
    
    return text,image


def choose_one_captcha_text_and_image(pics_dir=PICS_DIR):
    """    while True:
        text, image = gen_captcha_text_and_image()
        if image.shape == (60, 160, 3):
            return text, image
    """
    pics_list= os.listdir(pics_dir)
    pic = random.choice(pics_list)
    # print(pic)

    return get_single_image_and_text(pic)


def convert2gray(img):
    if len(img.shape) > 2:
        gray = np.mean(img, -1)
        # 上面的转法较快，正规转法如下
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        return img


"""
cnn在图像大小是2的倍数时性能最高, 如果你用的图像大小不是2的倍数，可以在图像边缘补无用像素。
np.pad(image,((2,3),(2,2)), 'constant', constant_values=(255,))  # 在图像上补2行，下补3行，左补2行，右补2行
"""

# 文本转向量

CHAR_SET_LEN = len(CHAR_SET)


def text2vec(text):
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长4个字符')

    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)

    def char2pos(c):
        for i in range(0, len(CHAR_SET)):
            if CHAR_SET[i] == c:
                return i

    for i, c in enumerate(text):
        print(text,i,c)
        idx = i * CHAR_SET_LEN + char2pos(c)
        # print i,CHAR_SET_LEN,char2pos(c),idx
        vector[idx] = 1
    return vector

# print text2vec('1aZ_')

# 向量转回文本


def vec2text(vec):
    char_pos = vec.nonzero()[0]
    text = []
    for i, c in enumerate(char_pos):
        char_at_pos = i  # c/63
        char_idx = c % CHAR_SET_LEN
        # if char_idx < 10:
        #     char_code = char_idx + ord('0')
        # elif char_idx < 36:
        #     char_code = char_idx - 10 + ord('A')
        # elif char_idx < 62:
        #     char_code = char_idx - 36 + ord('a')
        # elif char_idx == 62:
        #     char_code = ord('_')
        # else:
        #     raise ValueError('error')
        text.append(CHAR_SET[char_idx])
    return "".join(text)


"""
#向量（大小MAX_CAPTCHA*CHAR_SET_LEN）用0,1编码 每63个编码一个字符，这样顺利有，字符也有
vec = text2vec("F5Sd")
text = vec2text(vec)
print(text)  # F5Sd
vec = text2vec("SFd5")
text = vec2text(vec)
print(text)  # SFd5
"""


# 生成一个训练batch
def get_next_batch(batch_size=128):
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT * IMAGE_WIDTH])
    batch_y = np.zeros([batch_size, MAX_CAPTCHA * CHAR_SET_LEN])



    for i in range(batch_size):
        text, image = choose_one_captcha_text_and_image()
        image = convert2gray(image)

        # (image.flatten()-128)/128  mean为0
        batch_x[i, :] = image.flatten() / 255
        batch_y[i, :] = text2vec(text)

    return batch_x, batch_y


####################################################################

X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32)  # dropout


# 定义CNN
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

    # w_c1_alpha = np.sqrt(2.0/(IMAGE_HEIGHT*IMAGE_WIDTH)) #
    # w_c2_alpha = np.sqrt(2.0/(3*3*32))
    # w_c3_alpha = np.sqrt(2.0/(3*3*64))
    # w_d1_alpha = np.sqrt(2.0/(8*32*64))
    # out_alpha = np.sqrt(2.0/1024)

    # 3 conv layer
    w_c1 = tf.Variable(w_alpha * tf.random_normal([3, 3, 1, 32]))
    b_c1 = tf.Variable(b_alpha * tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(
        x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[
                           1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob)

    w_c2 = tf.Variable(w_alpha * tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(
        conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[
                           1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)

    w_c3 = tf.Variable(w_alpha * tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(
        conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[
                           1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)

    # Fully connected layer
    w_d = tf.Variable(w_alpha * tf.random_normal([8 * 32 * 40, 1024]))
    b_d = tf.Variable(b_alpha * tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)

    w_out = tf.Variable(
        w_alpha * tf.random_normal([1024, MAX_CAPTCHA * CHAR_SET_LEN]))
    b_out = tf.Variable(
        b_alpha * tf.random_normal([MAX_CAPTCHA * CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)
    # out = tf.nn.softmax(out)
    return out


# 训练
def train_crack_captcha_cnn():
    import time
    start_time = time.time()
    output = crack_captcha_cnn()
    # loss
    #loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(output, Y))
    loss = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    # 最后一层用来分类的softmax和sigmoid有什么不同？
    # optimizer 为了加快训练 learning_rate应该开始大，然后慢慢衰
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
    # 创建一个saver对象用来保存训练的数据、模型，   此处默认参数 max_to_keep=1，即只保存最新的训练模型
    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        step = 0
        while True:
            batch_x, batch_y = get_next_batch(64)

            _, loss_ = sess.run([optimizer, loss], feed_dict={
                                X: batch_x, Y: batch_y, keep_prob: 0.75})
            print(time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(time.time())), step, loss_)

            # 每100 step计算一次准确率
            if step % 100 == 0:
                batch_x_test, batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={
                               X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print('***************************************************************第%s次的准确率为%s' % (step, acc*100))
                # 如果准确率大于50%,保存模型,完成训练
                if acc > 0.9:  # 我这里设了0.9，设得越大训练要花的时间越长，如果设得过于接近1，很难达到。如果使用cpu，花的时间很长，cpu占用很高电脑发烫。
                    # 使用saver对象保存此模型
                    saver.save(sess, "crack_capcha.model", global_step=step)
                    print(time.time()-start_time)
                    break

            step += 1


if __name__ == "__main__":
    #train_crack_captcha_cnn()
    
    output = crack_captcha_cnn()

 
    #W = tf.Variable(np.arange(6).reshape((2, 3)), dtype=tf.float32, name="weights")
    #b = tf.Variable(np.arange(3).reshape((1, 3)), dtype=tf.float32, name="biases")


    with tf.Session() as sess:  # 创建会话
        # 在会话中恢复当前目录下最新保存的模型，
        #saver = tf.train.import_meta_graph('crack_capcha.model-1800.meta')

        saver = tf.train.Saver()  # 创建saver对象
        #saver.restore(sess,"crack_capcha.model")
        saver.restore(sess, tf.train.latest_checkpoint('.'))

        ok = 0
        need_verify=os.listdir("verify_pic_set") 

        for pic in need_verify:
            pic_name=os.path.join("verify_pic_set",pic)
            text, image = get_single_image_and_text(pic_name)
            image = convert2gray(image)
            image = image.flatten() / 255

            predict = tf.argmax(tf.reshape(
                output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
            text_list = sess.run(predict, feed_dict={X: [image], keep_prob: 1})
            predict_text = text_list[0].tolist()
            print(text_list)
            print(predict)
            vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
            i = 0
            try:
                for t in predict_text:
                    vector[i * CHAR_SET_LEN + t] = 1
                    i += 1
                    # break
                print("正确: {}  预测: {}".format(text, vec2text(vector)))
                if text == vec2text(vector):
                    ok += 1
            except:
                traceback.print_exc()
                print("predict_text",predict_text)                
            
        print("正确率:%f", ok/len(need_verify))
        
