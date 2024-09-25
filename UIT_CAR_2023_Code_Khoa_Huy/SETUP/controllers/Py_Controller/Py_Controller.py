from controller import Robot
from controller import Motor
from controller import DistanceSensor
from controller import Camera
from controller import LED
from controller import Supervisor
import math
#---------------Khởi tạo thông tin robot---------------#
# KHÔNG CHỈNH SỬA TIME_STEP !!!
# Robot
robot = Robot()
# Time step
TIME_STEP = 8
# Camera     
cam = robot.getDevice("camera")
# Leff motor, Right motor   
lm = robot.getDevice("left wheel motor")
rm = robot.getDevice("right wheel motor")
# Sensors
NB_GROUND_SENS = 8
gs = []
gsNames = [
    'gs0', 'gs1', 'gs2', 'gs3',
    'gs4', 'gs5', 'gs6', 'gs7'
]
ds = robot.getDevice("ds_center")
# LEDs
NB_LEDS = 5
leds = []
led_Names = [
    'led0', 'led1', 'led2', 'led3', 'led4'
]
# Hàm đợi để khởi tạo robot
# KHÔNG ĐƯỢC CHỈNH SỬA!!!
initTime = robot.getTime()
while robot.step(TIME_STEP) != -1:
    if (robot.getTime() - initTime) * 1000.0 > 200:
        break

#---------------Phần code code set up---------------#

# Time step
robot.step(TIME_STEP)

# Motor
lm.setPosition(float("inf"))
lm.setVelocity(0)
rm.setPosition(float("inf"))
rm.setVelocity(0)

# Camera
cam.enable(64)

# Sensors
for i in range(NB_GROUND_SENS):
    gs.append(robot.getDevice(gsNames[i]))
    gs[i].enable(TIME_STEP)


ds.enable(TIME_STEP)


# LEDs    
for i in range(NB_LEDS):
    leds.append(robot.getDevice(led_Names[i]))

# Điều khiển LED
def LED_Alert():
    if (robot.getTime() - initTime)*1000 % 3000 >= 2000:
        leds[1].set(1)
    return




#-------------------Định nghĩa-------------------#
# Tín hiệu của xe
NOP = 0.1
MID = 0

LECHTRAI1 = 1
LECHPHAI1 = -1
LECHTRAI2 = 2
LECHPHAI2 = -3
LECHTRAI3 = 4
LECHPHAI3 = -4

LECHTRAINANG = 5
LECHPHAINANG = -5

LEFT = 6
RIGHT = -6

FULL_SIGNAL  = 7
BLANK_SIGNAL = -8
Pre_pos = 0 
a = 0
d = 0
x = 0
c = 0
e = 0
f = 0
g = 0
time = 0
Max = 33 # Max speed
Min = 20 # Min speed
Status = 0
Speed = 0
threshold = [300 , 300 , 300 , 300 , 300 , 300 , 300 , 300]
preFilted = 0b00000000
# Velocities
left_ratio = 0.0
right_ratio = 0.0
#-------------Phần code điều khiển xe-------------#
# Hàm đọc giá trị của sensors
def ReadSensors():
    gsValues = []
    filted = 0x00
    for i in range(NB_GROUND_SENS):
        gsValues.append(gs[i].getValue())
        if gsValues[i] < threshold[i]:
            filted |= (0x01 << (NB_GROUND_SENS - i - 1))
    return filted



# Trả về vi trí của xe
def DeterminePosition(filted):

    if filted == 0b00011000:
        return MID
    
    elif filted == 0b00010000:
        return LECHPHAI1
    elif filted == 0b00001000:
        return LECHTRAI1    
    
    elif filted in [0b00110000]:
        return LECHPHAI2
    elif filted in [0b00001100]:
        return LECHTRAI2
    
    elif filted in [0b01100000,0b00100000]:
        return LECHPHAI3
    elif filted in [0b00000110,0b00000100]:
        return LECHTRAI3

    elif filted in [0b11000000,0b10000000,0b01000000]:
        return LECHPHAINANG
    elif filted in [0b00000011,0b00000001,0b00000010]:
        return LECHTRAINANG
    
    elif filted in [0b01110000,0b11111000,0b11110000,0b11100000]:
        return LEFT
    elif filted in [0b00001110,0b00011111,0b00001111,0b00000111]:
        return RIGHT
    
    elif filted in [0b11111111,0b01111110,0b01111111,0b11111110]:
        return FULL_SIGNAL
    elif filted in [0b00000000]:
        return BLANK_SIGNAL

    return NOP
    
#-------------Main loop-------------#

# Chương trình sẽ được lặp lại vô tận 
while robot.step(TIME_STEP) != -1:
    time = time + 1
    filted = ReadSensors()
    global ds_value
    dis = ds.getValue()
    #pos: position - lấy vị trí của xe
    pos = DeterminePosition(filted)
    # In ra màn hình giá trị của filted ở dạng nhị phân
    print(" ")
    print('Pos: ' + str(format(filted, '08b')), end='   ')
    print(f"Status: {Status}", end='   ')
    print(left_ratio * Speed, right_ratio * Speed)
    print(f"a: = {a}  d: = {d}  x: = {x}  e: = {e}  c: = {c}  f: = {f}  Pre_pos: = {Pre_pos}  Dis = {dis-dis % 1}  Time = {time}")

    # a tín hiệu cua
    # d tín hiệu line đen
    # x phân biệt cua thường và cua có th
    # e đi xuyến
    # c biến đếm
    # f biến để ra xuyến
    # Pre_pos trạng thái xe trước đó
    
    
    if g == 1:# hàm set lại thời gian
        time = 0
        g = 0
        
    if e == 1 and time > 25 and Status not in ["đi xuyến","đi xuyến vật cản"]:# hàm tránh nhiễu
        e = 0
    if 0 < a < 3 and time > 35 and Status not in ["cua trái","cua phải","cua trái th","cua phải th","cua trái vật cản","cua phải vật cản"]:# hàm tránh nhiễu
        a = 0
               
    #Điều khiển xe
    if pos == FULL_SIGNAL and c == 0:
        d = 1
    elif pos == BLANK_SIGNAL:
        Pre_pos = 0.1
        
    elif pos == LEFT and x == 0 and 800 < dis < 1000:
        a = 3
        x = 1 
    elif pos == RIGHT and x == 0 and 800 < dis < 1000:
        a = 4
        x = 1 
        
    elif pos == LEFT and x == 0 and a != 2 and Pre_pos != 0.1:# cua trái thường
        Pre_pos = 7
        a = 1
        x = 1
    elif pos == RIGHT and x == 0 and a != 1 and Pre_pos != 0.1:# cua phải thường
        Pre_pos = 8
        a = 2
        x = 1
        
    elif e == 1 and x == 0 and 500 < dis < 1000 and c == 0 : #xuyến vật cản
        e = 1
        d = 2 

        
          
    if a == 0 and d == 1 and e != 1: #hàm dừng xe
        Speed = Max
        c = c + 1
        if c < 5:
            Status = "đang xem xét"
            left_ratio, right_ratio = 2, 2
        elif pos != FULL_SIGNAL:
            e = 1 # vào xuyến
            g = 1
            d = 0
            c = 0 
        elif c <= 25 and pos == FULL_SIGNAL:
            left_ratio, right_ratio = 1, 1
        else:
            Status = "ngon"
            left_ratio, right_ratio = 0, 0

     
    elif a < 3: # ra xuyến              
        if filted in [0b00011110,0b00011110,
        0b00110111,0b00010111,0b00011111,0b00111110,
        0b00010001,0b00110011,0b00010011] and f == 1:
            Status = "ra xuyến"
            a = 2
            d = 1
            c = 0
            
        if (pos == MID and d != 1 and x != 1) or (0 < Pre_pos < 2 and pos == BLANK_SIGNAL and a == 0):      
            Status = "thẳng"
            Speed = Max
            Pre_pos = 0.5
            left_ratio, right_ratio = 2,2

        if pos == LECHPHAI1 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch phải 1"
            Pre_pos = 1
            left_ratio, right_ratio = 1.5,2.2
        elif pos == LECHTRAI1 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch trái 1"
            Pre_pos = 1
            left_ratio, right_ratio = 2.2,1.5

        elif pos == LECHPHAI2 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch phải 2"
            Pre_pos = 2
            left_ratio, right_ratio = 1,2.5
        elif pos == LECHTRAI2 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch trái 2"
            Pre_pos = 2
            left_ratio, right_ratio = 2.5,1
            
        elif pos == LECHPHAI3 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch phải 3"
            Pre_pos = 3
            left_ratio, right_ratio = 0.2,3
        elif pos == LECHTRAI3 and d != 1 and x != 1:
            Speed = Max
            Status = "lệch trái 3"
            Pre_pos = 3
            left_ratio, right_ratio = 3,0.2

        elif (pos == LECHPHAINANG and d != 1 and x != 1):
            Status = "lệch phải nặng"
            Speed = Max 
            Pre_pos = 5                       
            left_ratio, right_ratio = 0.11,3.2
        elif (pos == LECHTRAINANG and d != 1 and x != 1):
            Status = "lệch trái nặng" 
            Speed = Max            
            Pre_pos = 6
            left_ratio, right_ratio = 3.2,0.11
    
    
        elif (a == 1 and x == 1 and d != 1) or (Pre_pos == 5 and pos == BLANK_SIGNAL and a == 0):
            Status = "cua trái"
            Speed = Min
            time = 0
            c = c + 1
            if pos == FULL_SIGNAL:
                d = 1
                a = 0
                x = 0
            if c < 5 :
                left_ratio, right_ratio = 1,1
            elif 5 == c and pos != BLANK_SIGNAL:
                x = 0
                c = 0
                e = 0
            else:
                if c < 22 :
                    left_ratio, right_ratio = 1,1
                elif 22 <= c < 27:
                    left_ratio, right_ratio = 0,0
                elif 27 <= c:
                    if pos not in [MID,LECHPHAI1,LECHPHAI2,LECHPHAI3]:
                        left_ratio, right_ratio = -1,1
                    else:
                        if c <= 75:
                            left_ratio, right_ratio = 0,0
                        if c > 75:
                            a = 0
                            x = 0
                            c = 0
        elif a == 1 and d == 1:
            Status = "cua trái th"
            if Pre_pos != 7 or f == 1:
                Speed = Min
                c = c + 1
                if c < 22 :
                    left_ratio, right_ratio = 1,1
                elif 22 <= c < 27:
                    left_ratio, right_ratio = 0,0
                elif 27 <= c < 50:
                    left_ratio, right_ratio = -1,1
                elif c > 50:
                    if pos not in [MID,LECHPHAI1,LECHPHAI2,LECHPHAI3]:
                        left_ratio, right_ratio = -1,1
                    else:
                        if c <= 73:
                            left_ratio, right_ratio = 0,0
                        if c > 73:
                            a = 0
                            x = 0
                            f = 0
                            c = 0
                            d = 0
            else:
                a = 0
                
                
        elif (a == 2 and x == 1 and d != 1) or (Pre_pos == 6 and pos == BLANK_SIGNAL and a == 0):
            Status = "cua phải"
            Speed = Min
            time = 0
            c = c + 1
            if pos == FULL_SIGNAL:
                d = 1
                a = 0
                x = 0
            if c < 5 :
                left_ratio, right_ratio = 1,1
            elif 5 == c and pos != BLANK_SIGNAL:
                x = 0
                c = 0
                e = 0
            else:
                if c < 22 :
                    left_ratio, right_ratio = 1,1
                elif 22 <= c < 27:
                    left_ratio, right_ratio = 0,0
                elif 27 <= c:
                    if pos not in [MID,LECHTRAI1,LECHTRAI2,LECHTRAI3]:
                        left_ratio, right_ratio = 1,-1
                    else:
                        if c <= 75:
                            left_ratio, right_ratio = 0,0
                        if c > 75:
                            a = 0
                            x = 0
                            c = 0
        elif a == 2 and d == 1:
            Status = "cua phải th"
            if Pre_pos != 8 or f == 1:
                Speed = Min
                c = c + 1
                if c < 22 :
                    left_ratio, right_ratio = 1,1
                elif 22 <= c < 27:
                    left_ratio, right_ratio = 0,0
                elif 27 <= c < 50:
                    left_ratio, right_ratio = 1,-1
                elif c > 50:
                    if pos not in [MID,LECHTRAI1,LECHTRAI2,LECHTRAI3]:
                        left_ratio, right_ratio = 1,-1
                    else:
                        if c <= 73:
                            left_ratio, right_ratio = 0,0
                        if c > 73:
                            a = 0
                            x = 0
                            f = 0
                            c = 0
                            d = 0
            else:
                a = 0
                   
    
    elif e != 1 and a == 4:
        Status = "cua phải vật cản"
        Speed = Min
        c = c + 1        
        if c < 40:
            left_ratio, right_ratio = 1,1
        if 40 <= c < 45:
            left_ratio, right_ratio = 0,0
        if 45 <= c < 81:
            left_ratio, right_ratio = 1,-1
        if 81 <= c < 86:
            left_ratio, right_ratio = 0,0
        if 86 <= c:
            left_ratio, right_ratio = 3,3
        if 100 < c:
            left_ratio, right_ratio = 3,3
            if pos != BLANK_SIGNAL:
                a = 1 
                d = 1
                c = 0
                
    elif e != 1 and a == 3:
        Status = "cua trái vật cản"
        Speed = Min
        c = c + 1        
        if c < 40:
            left_ratio, right_ratio = 1,1
        if 40 <= c < 45:
            left_ratio, right_ratio = 0,0
        if 45 <= c < 81:
            left_ratio, right_ratio = -1,1
        if 81 <= c < 86:
            left_ratio, right_ratio = 0,0
        if 86 <= c:
            left_ratio, right_ratio = 3,3
        if 100 < c:
            left_ratio, right_ratio = 3,3
            if pos != BLANK_SIGNAL:
                a = 2 
                d = 1
                c = 0

    
    if e == 1 and d == 1:
        Status = "đi xuyến"
        Speed = Max
        c = c + 1
        if c < 5 :
            left_ratio, right_ratio = 1,1
        elif 5 == c and pos != BLANK_SIGNAL:
             a = 0 
             d = 0
             c = 0
             x = 0
             e = 0
             f = 0 
        else:
             if c < 12 :
                 left_ratio, right_ratio = 1,1
             elif 12 <= c < 17 and pos == BLANK_SIGNAL:
                 left_ratio, right_ratio = 0,0
             elif 17 <= c:
                 if pos not in [MID,LECHTRAI1,LECHTRAI2]:
                     left_ratio, right_ratio = 0.5,-0.5
                 else:
                     if c <= 63:
                         left_ratio, right_ratio = 0,0
                     if c > 63:
                         a = 0 
                         d = 0
                         c = 5
                         x = 0
                         e = 0
                         f = 1
             else: 
                 a = 0 
                 d = 0
                 c = 0
                 x = 0
                 e = 0
                 f = 0

    if e == 1 and d == 2 and pos == BLANK_SIGNAL:
        Status = "đi xuyến vật cản"
        Speed = Max
        c = c + 1
        if c < 20 :
            left_ratio, right_ratio = 1,1
        elif c == 20 and pos != BLANK_SIGNAL:
             a = 0 
             d = 0
             c = 0
             x = 0
             e = 0
             f = 0  
        else:
             f = 1
             if c < 30 :
                 left_ratio, right_ratio = 1,1
             if 30 <= c < 35:
                 left_ratio, right_ratio = 0,0
             if 35 <= c < 75:
                 left_ratio, right_ratio = 0.5,-0.5
             if 75 <= c < 80:
                 left_ratio, right_ratio = 0,0
             if 80 <= c:
                 left_ratio, right_ratio = 1,1+c/500
             if pos != BLANK_SIGNAL:
                a = 0
                d = 0
                c = 5
                x = 0
                e = 0   



    lm.setVelocity(left_ratio * Speed)  # set vận tốc cho bánh xe trái
    rm.setVelocity(right_ratio * Speed) # set vận tốc cho bánh xe phải
pass