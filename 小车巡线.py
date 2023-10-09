# Untitled - By: User - 周三 4月 19 2023
import time
import sensor, image,lcd
from machine import UART #串口库函数
from fpioa_manager import fm # GPIO重定向函数
from Maix import GPIO
from fpioa_manager import fm

fm.register(12, fm.fpioa.GPIO0)
LED_B = GPIO(GPIO.GPIO0, GPIO.OUT) #构建LED对象
LED_B.value(0) #点亮LED

fm.register(7, fm.fpioa.GPIO0)
led_b=GPIO(GPIO.GPIO0, GPIO.OUT)

#映射串口引脚
fm.register(24, fm.fpioa.UART1_TX, force=True)
fm.register(25, fm.fpioa.UART1_RX, force=True)
uart1 = UART(UART.UART1,9600, 8, 0, 1, timeout=1000, read_buf_len=4096)

green_threshold = ((0, 80))           #黑色50
roi1            = [0,100,320,16]       #巡线敏感区
roi2            = [0,180,320,8]        #关键点敏感区
expectedValue   = 160                  #巡线位置期望
err             = 0                    #本次误差
old_err         = 0                    #上次误差
Kp              = 0.002                 #PID比例系数
Kd              = 0.02                    #PID微分系数
Speed           = 2                    #期望速度
Speed_left      = 0                    #左轮速度
Speed_right     = 0                    #右轮速度
Flag            = 0                    #用于关键点标志
x_pos1          = 160                  #初始横坐标
x_pos2          = 160                  #初始横坐标

lcd.init()
sensor.reset()#初始化摄像头
sensor.set_pixformat(sensor.GRAYSCALE)#设置摄像头格式为像素模式
sensor.set_framesize(sensor.QVGA) # 320x240
sensor.skip_frames(time = 3000 )#跳过3000张图片
sensor.set_auto_gain(False) # 增益关闭，在使用颜色追踪时，需要关闭自动增益。
sensor.set_auto_whitebal(False) # 白平衡关闭，在使用颜色追踪时，需要关闭自动白平衡。
#sensor.set_hmirror(True)#水平方向翻转
#sensor.set_vflip(True)#垂直方向翻转
sensor.run(1)

while (True):
    img=sensor.snapshot()#摄像头拍照，并返回img图像
    img.draw_arrow(160, 170, 160, 120, color = (255, 255, 255), size =20, thickness = 4)#中心箭头
    img.draw_arrow(10, 10, 10, 50, color = (255, 255, 255), size =10, thickness = 2)#y轴
    img.draw_arrow(10, 10, 50, 10, color = (255, 255, 255), size =10, thickness = 2)#x轴
    img.draw_string(20, 50, "y", color = (255, 255,255), scale = 2,mono_space = False)#y标注
    img.draw_string(50, 20, "x", color = (255, 255,255), scale = 2,mono_space = False)#x标注
    img.draw_string(250, 200, "YSK", color = (255, 255,255), scale = 3,mono_space = False)#水印
    statistics1 = img.find_blobs([green_threshold],roi=roi1,area_threshold=200,merge=True)#基础框
    statistics2 = img.find_blobs([green_threshold],roi=roi2,area_threshold=120,merge=True,margin=120)#感兴趣框
    if statistics1:
        for b in statistics1:
            tmp=img.draw_rectangle(b[0:4])#感兴趣框
            tmp1=img.draw_cross(b[5], b[6])
            x_pos1 = b[5]#中心位置x坐标
            y_pos1 = b[6]#中心位置y坐标
            X1 = '%03d' % x_pos1
            led_b.value(1)

            if b[2] > 100 and b[2] < 150 :
                    led_b.value(1)
                    Flag = 2

            elif b[2] > 150 :
                    led_b.value(1)
                    Flag = 3

            else :
                    Flag = 1
                    led_b.value(1)
                    time.sleep_ms(10)
                    led_b.value(0)
                    time.sleep_ms(10)



            '''
            #PID计算

            actualValue=b[5]
            err=actualValue-expectedValue
            Speed_left = ( Speed + (Kp*err+Kd*(err-old_err)))*100
            Speed_right = ( Speed - (Kp*err+Kd*(err-old_err)))*100
            old_err= err
            if Speed_left > 400:
                Speed_left =400
            elif Speed_left < 100:
                Speed_left = 100
            if Speed_right > 400:
                Speed_right = 400
            elif Speed_right < 100:
                Speed_right = 100
            spl = '%03d' % Speed_left
            spr = '%03d' % Speed_right
            F = '%d' % Flag
            DATA = 'F' + spl + spr + F + 'E'

            #print("Speed_left,Speed_right")
            print(int(Speed_left),int(Speed_right),int(Flag))
            '''
            F = '%d' % Flag
            DATA = 'F' + X1+ F + 'E'

    if statistics2:
        for b in statistics2:
            tmp=img.draw_rectangle(b[0:4])
            tmp=img.draw_cross(b[5], b[6])
            x_pos2 = b[5]#中心位置x坐标
            y_pos2= b[6]#中心位置y坐标
            X0 = '%03d' % x_pos2

    uart1.write( DATA )
    print(DATA)
    print(b[2])
    Flag = 0
    img.draw_string(2,190, ("X1:%03d" %(x_pos1)), color=(255,255,255), scale=2)
    img.draw_string(2,215, ("X0:%03d" %(x_pos2)), color=(255,255,255), scale=2)

    lcd.display(img)
