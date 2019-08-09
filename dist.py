import sensor, image, time, math
from pyb import UART
# 要使颜色识别准确，必须要确保环境光线处于稳定状态

def mean(L): # list
    return sum(L)/len(L)

# -------------------------------------- 初始化 ------------------------------------

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA)  # use QQVGA for speed.
sensor.skip_frames(10)              # Let new settings take affect.
sensor.set_auto_whitebal(False)     # turn this off.
clock = time.clock()                # Tracks FPS.

# -------------------------------------- 参数标定 ----------------------------------

K = 7050  # 测距比例，需要进行测量计算 300 * 23.5    距离 = 一个常数K/直径的像素    lenth 距离，Lm 像素点数

# red_threshold = (49, 26, 29, 123, 14, 86)
red_threshold = (51, 27, 28, 79, -15, 47)# 识别阈值，通过阈值设定工具获取阈值
#(46, 26, 29, 123, 14, 86)
# 串口一直是3，第二个参数是波特率
uart = UART(3, 115200, timeout_char=1000)

d = 0   # 距离
# --------------------------------------- 图像处理 ---------------------------------------

while(True):
    clock.tick() # 跟踪快照之间经过的毫秒数
    flag = 0

#    L = list()

    # 获取图像
    img = sensor.snapshot() # 截取帧缓冲区的图像
    blobs = img.find_blobs([red_threshold],pixels_threshold=20) # 返回一个包括每个色块的色块对象的列表。 空列表 -> False
    img.draw_cross(160, 120)  # 中心十字符号
    # 判断当前视野有无引导标识
    if blobs:   # 有
        # 如果视野中只有一个色块
        if len(blobs) == 1:
            flag = 0
            # Draw a rect around the blob.
            b = blobs[0]
            img.draw_rectangle(b[0:4])  # rect
            img.draw_cross(b[5], b[6])  # cx, cy

            x = b[5]
            y = b[6]
            print("色块中心点x："+str(b[5])+"y："+str(b[6]) + "\n")
            # TODO: 如果把下面的 像素量的计算方法换成 长×宽的计算方法会不会更好？
            Lm = (b[2]+b[3])/2          # b[2]长 b[3]宽  即长宽像素点的个数
            d = K/Lm        # d = K/Lm  300 * 23.5 = 7050
            print("距离：" + str(d) + "\n")
            #print("像素个数：" + str(Lm) + "\n")







            # 取高低位
            x1 = x & 0xff00
            x2 = x & 0x00ff

            y1 = y & 0xff00
            y2 = y & 0x00ff

            D1 = int(d) & 0xFF00
            D2 = int(d) & 0x00FF

            # 中心点x=80 y=60

            # 判断对齐
            print("色块中心点x:" + str(x))
            print("160")

            if abs(x-160) < 50:
                flag = 1
            print("对齐位：" + str(flag))


# -------------------------------------- 发送串口 -------------------------------
            # 包头        长度    x           y               d           flag  包尾
            # 0xA0 0xA1   0x07  0x00 0x11   0x00    0x22    0x01 0x2c   0x01    0x0D 0x0A
            #uart.write()
            start1 = 0xA0
            start2 = 0xA1
            lenth = 7

            end1 = 0x0D
            end2 = 0x0A

            datas = list()
            datas.append(start1)
            datas.append(start2)
            datas.append(lenth)
            datas.append(x2)
            datas.append(x1)
            datas.append(y2)
            datas.append(y1)
            datas.append(D2)
            datas.append(D1)
            datas.append(flag)
            datas.append(end1)
            datas.append(end2)

            print(datas)

            for i in datas:

                uart.writechar(i)
                print(str(hex(i)))
            time.sleep(100)

            flag = 0

# 如果有大于2个色块目标，蜂鸣器响，可能不准备写下面的蜂鸣器了
        else:
            pass    # 蜂鸣器响
            #uart.write("ring")

    else:       # 没有识别到引导标识
        pass    # 向左移到60° 再向右移动到120°
        #uart.write("not found")



# -------------------------------------- 扫描 ---------------------------------------
# 附加题2

# 环形靶 和 引导标识 距离定标点d = 250cm

def scan():
    pass

    # 1、初始化
    # 2、拍照
    # 3、当引导标识色块的中心x 与 像素中心点x 的差小于一定值时 串口发送信号

    #print(clock.fps())



    #find_blobs(thresholds, invert=False, roi=Auto),thresholds为颜色阈值，
    #是一个元组，需要用括号［ ］括起来。invert=1,反转颜色阈值，invert=False默认
    #不反转。roi设置颜色识别的视野区域，roi是一个元组， roi = (x, y, w, h)，代表
    #从左上顶点(x,y)开始的宽为w高为h的矩形区域，roi不设置的话默认为整个图像视野。
    #这个函数返回一个列表，[0]代表识别到的目标颜色区域左上顶点的x坐标，［1］代表
    #左上顶点y坐标，［2］代表目标区域的宽，［3］代表目标区域的高，［4］代表目标
    #区域像素点的个数，［5］代表目标区域的中心点x坐标，［6］代表目标区域中心点y坐标，
    #［7］代表目标颜色区域的旋转角度（是弧度值，浮点型，列表其他元素是整型），
    #［8］代表与此目标区域交叉的目标个数，［9］代表颜色的编号（它可以用来分辨这个
    #区域是用哪个颜色阈值threshold识别出来的）。


# 协议:  包头： 0xA0 0xA1

#       (第三位)数据长度:

#       中间数据：

#       包尾: 0x0D 0x0A

