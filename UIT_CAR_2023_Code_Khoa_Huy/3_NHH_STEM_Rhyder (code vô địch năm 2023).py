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
    
# LEDs    
for i in range(NB_LEDS):
    leds.append(robot.getDevice(led_Names[i]))

# Điều khiển LED
def LED_Alert():
    if (robot.getTime() - initTime)*1000 % 3000 >= 2000:
        #leds[1].set(not(leds[1].get()))
        leds[1].set(1)
        #for i in range(NB_LEDS):
            #leds[i].set(not(leds[i].get()))
    return

#-------------------Định nghĩa-------------------#

# Tín hiệu của xe
NOP = -1
MID = 0
LEFT = 1
RIGHT = -1
FULL_SIGNAL  = 2
BLANK_SIGNAL = -2
ROUNDABOUTHAVINGBLOCK = 200
MAX_SPEED = 0
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
        if gsValues[i] > threshold[i]:
            filted |= (0x01 << (NB_GROUND_SENS - i - 1))
    #print(*gsValues, sep = '\t')
    return filted

# Trả về vi trí của xe
def DeterminePosition(filted):
    if filted == 0b11100111 or filted == 0b11101111 or filted == 0b11110111 or filted == 0b00010111:
        return MID
    elif filted == 0b10011111 or filted == 0b10111111 or filted == 0b11011111 or filted == 0b00111111 or filted == 0b01111111 or filted == 0b10111111 or filted == 0b11001111 or filted == 0b11011111:
        return RIGHT
    elif filted == 0b11111100 or filted == 0b11111110 or filted == 0b11111101 or filted == 0b11111001 or filted == 0b11111011 or filted == 0b11111101 or filted == 0b11110011 or filted == 0b11111011:
        return LEFT
    elif filted == 0b00000000:
        return FULL_SIGNAL
    elif filted == 0b11111111:
        return BLANK_SIGNAL
    return NOP

#các hàm điều khiển xe di chuyển
def GoStraight(filted):
    if filted == 0b11100111:
        return 1.1, 1.1

    elif filted == 0b11101111:
        return 1.05,1.1
    elif filted == 0b11110111:
        return 1.1,1.05
    return 1.1, 1.1

def GoStraightHavingBlock(filted):
    if filted == 0b11100111:
        return 0.4*1.3,0.4*1.3
    elif filted == 0b11110111 or filted == 0b11110011 or filted == 0b11111001 or filted == 0b11111101 or filted == 0b11111100 or filted == 0b11111110:
        return 0.3*1.3,0.15*1.3
    elif filted == 0b11101111 or filted == 0b11001111 or filted == 0b11011111 or filted == 0b10011111 or filted == 0b10111111 or filted == 0b00111111 or filted == 0b01111111:
        return 0.15*1.3,0.3*1.3
    return 0.2*1.3,0.2*1.3

def GoStraightPreIntersection(filted, r = 0.25, MAXSPEED = MAX_SPEED, fix = 17, ratio = 21/22):
    if filted == 0b11100111:
        return fix/MAXSPEED, fix/MAXSPEED

    elif filted == 0b11101111:
        return (fix/MAXSPEED)*ratio,fix/MAXSPEED
    elif filted == 0b11110111:
        return fix/MAXSPEED,(fix/MAXSPEED)*ratio
    return 1.1*r, 1.1*r

def TurnLeft(filted):
    if filted == 0b00111111 or filted == 0b01111111 or filted == 0b10111111:
        return 0,1.2
    elif filted == 0b10011111 or filted == 0b10111111 or filted == 0b11011111:
        return 0.5,1.4
    elif filted == 0b11001111 or filted == 0b11011111:
        return 0.8,1
    return 1,1

def TurnRight(filted):
    if filted == 0b11111100 or filted == 0b11111110 or filted == 0b11111101:
        return 1.2,0
    elif filted == 0b11111001 or filted == 0b11111011 or filted == 0b11111101:
        return 1.4,0.5
    elif filted == 0b11110011 or filted == 0b11111011:
        return 1,0.8
    return 1,1
    
    
def TurnLeftCorner(MAXSPEED,r = 15):
    return -r/MAXSPEED,(r/MAXSPEED)+0.08

def TurnRightCorner(MAXSPEED, r = 15):
    return (r/MAXSPEED)+0.08,-r/MAXSPEED

def TurnLeftIntersection():
    return 0.0,0.8

def TurnRightIntersection():
    return 0.8,0.0

def RunningBlankSignal(preFilted):
    if preFilted == 0b11001111 or preFilted == 0b11110011 or preFilted == 0b11011111 or preFilted == 0b11111011:
        if preFilted == 0b11001111 or preFilted == 0b11011111:
            return 1,1.05
        elif preFilted == 0b11110011 or preFilted == 0b11111011:
            return 1.05,1
    elif preFilted == 0b01111111 or preFilted == 0b00111111 or preFilted == 0b11111110 or preFilted == 0b11111100:
        if preFilted == 0b01111111 or preFilted == 0b00111111:
            return 1,1.05
        elif preFilted == 0b11111110 or preFilted == 0b11111100:
            return 1.05,1
    return 1.1,1.1




intersectiondirect = 0
e = 0
g = 0

l = 0
limitStop = 10
intersection_limit = 25
d = 0
a = 0
t = 0
t_ = 0
k = 5
midMAX = 0
m = -3/5
n = 70
a,aa=0,0
ROUNDABOUT=100
time = 0
i = 10
ii = 10
iii=10
iiii=30
intersectionConstruction=0
out_construction = 0
state = 0
time_ = 0
fulllineTime = 0
timeOnBridge = 0
upBridge = 80
straightBridge = 52
downBridge = 52
firstConnection = 50
secondConnection = 45
blockStep=0
delta = 0


#-------------Main loop-------------#

# Chương trình sẽ được lặp lại vô tận 
while robot.step(TIME_STEP) != -1:
    
    filted = ReadSensors()
    #pos: position - lấy vị trí của xe
    pos = DeterminePosition(filted)
    #
    ds = robot.getDevice("ds_center")
    ds.enable(TIME_STEP)
    distance = ds.getValue()

    # In ra màn hình giá trị của filted ở dạng nhị phân
    # print('Position: ' + str(format(filted, '08b')), sep = '\t')
    
    # print("d =",d)
    # print("e =:",e)
    # print(left_ratio, right_ratio)
    
    # print("intersectiondirect =",intersectiondirect)
    # print("d =",d)
    # print("out_construction =",out_construction)
    # print("left =",left_ratio, "right =",right_ratio)
    # print(time)
    if filted == 0b11100111 or filted == 0b11101111 or filted == 0b11110111 or filted == 0b01110111 or filted == 0b00010111 or filted == 0b00110111 or filted == 0b01100111 or filted == 0b00100111 or filted == 0b11110100 or filted == 0b11100110 or filted == 0b11110110 or filted == 0b00101111 or filted == 0b11101000 or filted == 0b11101100 or filted == 0b01101111 or filted == 0b11101110 or filted == 0b00110011 or filted == 0b00010011 or filted == 0b11001111:
        if preFilted == 0b00000111 or preFilted == 0b00001111 or preFilted == 0b00000011 or preFilted == 0b10000011:
            intersectiondirect = LEFT
        elif preFilted == 0b11100000 or preFilted == 0b11110000 or preFilted == 0b11100100 or preFilted == 0b11000000:
            intersectiondirect = RIGHT
    if pos == BLANK_SIGNAL:
        MAX_SPEED = 53
    elif pos == MID:
        MAX_SPEED = 59
        midMAX = MAX_SPEED
    else:
        MAX_SPEED = 62
    if a == 3: MAX_SPEED = 50


    if out_construction !=0:
        limit = 65
    else:
        limit=0

    if a + aa + d+e+intersectiondirect==0:
        state = "NORMAL"
    else:
        state = "ABNORMAL"
    # print(state)
    #Điều khiển xe
    if filted == 0b00010111:
        if preFilted == 0b10000000:filted = 0b00000000
    if pos == MID:
        
        if preFilted == 0b00000111 or preFilted == 0b00001111 or preFilted == 0b00011111 or preFilted == 0b00000011:
            intersectiondirect = LEFT
        elif preFilted == 0b11111000 or preFilted == 0b11110000 or preFilted == 0b11100000 or preFilted == 0b11000000:
            intersectiondirect == RIGHT
        if intersectiondirect == LEFT or intersectiondirect == RIGHT:
            left_ratio, right_ratio = GoStraightPreIntersection(filted, r = 0.25, MAXSPEED = MAX_SPEED, fix = 25, ratio = 21/22)
        elif intersectiondirect == 0:
            left_ratio, right_ratio = GoStraight(filted)
    
    elif pos == LEFT:
        left_ratio, right_ratio = TurnRight(filted)
    elif pos == RIGHT:
        left_ratio, right_ratio = TurnLeft(filted)

    elif pos == BLANK_SIGNAL and intersectiondirect!=ROUNDABOUT:
        e += 1
        if preFilted == 0b00011111 or preFilted == 0b01111111 or preFilted == 0b00000111 or preFilted == 0b00111111 or preFilted == 0b00001111:
            d = LEFT
        elif preFilted == 0b11100000 or preFilted == 0b11111110 or preFilted == 0b11111000 or preFilted == 0b11111100 or preFilted == 0b11110000:
            d = RIGHT
        elif preFilted != 0b11111111:
            e -= e
            left_ratio, right_ratio = RunningBlankSignal(preFilted)
        
        
                
    
    elif pos == FULL_SIGNAL:
        a-=a
        if intersectiondirect == LEFT:
            a = LEFT
        elif intersectiondirect == RIGHT:
            a = RIGHT
        elif intersectiondirect == 0:
            a = 0



    #ROUNDABOUT
    if filted == 0b00000000 and a == 0 and preFilted != 0b11111111:
        intersectiondirect = ROUNDABOUT
    if intersectiondirect == ROUNDABOUT or intersectiondirect==ROUNDABOUTHAVINGBLOCK:
        left_ratio, right_ratio = 30/MAX_SPEED,30/MAX_SPEED
    if intersectiondirect == ROUNDABOUT and filted == 0b11111111:
        a = 3
    if filted == 0b11111111 and a == 3:
        fulllineTime-=fulllineTime
        intersectiondirect = 0
        left_ratio, right_ratio = 1,-1

    if a == 3:
        turnLimit = 50
        if filted == 0b11000000 or filted == 0b11001110 or filted == 0b11001100 or filted == 0b11001000 or filted == 0b11101000 or filted == 0b11011000 or filted == 0b10011100 or filted == 0b10011001 or filted == 0b10111110 or filted == 0b11000111 or filted == 0b11000001 or filted == 0b11000011 or filted == 0b11010001 or filted == 0b10011000 or filted == 0b10111100 or filted == 0b11010000 or filted == 0b10010001 or filted == 0b11011001 or filted == 0b10010011 or filted == 0b10000011 or filted == 0b10011110 or filted == 0b11011100 or filted == 0b11011110 or filted == 0b11010011 or filted == 0b1000011 or filted == 0b00111100 or filted == 0b01111110 or filted == 0b01111100 or filted == 0b10111000 or filted == 0b10000001 or filted == 0b10000111 or filted == 0b10111001 or filted == 0b11100000:
            if preFilted == 0b11100000 or preFilted == 0b11000000 or preFilted == 0b11001110 or preFilted == 0b11001100 or preFilted == 0b11001000 or preFilted == 0b11101000 or preFilted == 0b11011000 or preFilted == 0b10011100 or preFilted == 0b10011001 or preFilted == 0b10111110 or preFilted == 0b11000111 or preFilted == 0b11000001 or preFilted == 0b11000011 or preFilted == 0b11010001 or preFilted == 0b10011000 or preFilted == 0b10111100 or preFilted == 0b11010000 or preFilted == 0b10010001 or preFilted == 0b11011001 or preFilted == 0b10010011 or preFilted == 0b10000011 or preFilted == 0b10011110 or preFilted == 0b11011100 or preFilted == 0b11011110 or preFilted == 0b11010011 or preFilted == 0b10000111 or preFilted == 0b00111100 or preFilted == 0b01111110 or preFilted == 0b01111100 or preFilted == 0b10111000 or preFilted == 0b10000001 or preFilted == 0b10111001:
                aa += 0
            else:
                aa += 1
        if aa>=1:
            time += 1
            if time >=0 and time <= 10: left_ratio, right_ratio = 0,0
            elif time > 10 and time <= turnLimit:
                d-=d
                left_ratio, right_ratio = 20/MAX_SPEED, 10/MAX_SPEED
            else:
                aa-=aa
                a-=a
                time-=time
                time_-=time_
                d=RIGHT
                e=limit
                # left_ratio, right_ratio = TurnRightCorner(MAXSPEED=MAX_SPEED)
                # if pos==MID:
                #     time_ +=1
                #     if time_ <=20 and time_>0:left_ratio, right_ratio = 0,0
                #     else:
                #         aa-=aa
                #         a-=a
                #         time-=time
                #         time_-=time_
                        
            
            # left_ratio, right_ratio = 0.8,0.2
            # if filted == 0b11111100 or filted == 0b11111011 or filted == 0b11111001 or filted == 0b11111110:
            #     aa = 0
            #     a = 0

    #-------------------------------------------------------------
    #INTERSECTION

    if a == LEFT:
        g += 1
        if g <= intersection_limit: left_ratio, right_ratio = GoStraightPreIntersection(filted, r = 0.25, MAXSPEED = MAX_SPEED, fix = 30, ratio = 21/22)
        else: 
            left_ratio, right_ratio = TurnLeftCorner(MAXSPEED=MAX_SPEED )
            if pos == BLANK_SIGNAL:
                g -=g
                e = limit+1
                d = a
                a -= a
                intersectiondirect -= intersectiondirect
                fulllineTime-=fulllineTime
        # left_ratio, right_ratio = TurnLeftIntersection()
        # if filted == 0b00111111:
        #     a = 0
        #     intersectiondirect = 0
        #     d = 0
    elif a == RIGHT:
        g += 1
        if g <= intersection_limit: left_ratio, right_ratio = GoStraightPreIntersection(filted, r = 0.25, MAXSPEED = MAX_SPEED, fix = 30, ratio = 21/22)
        else: 
            left_ratio, right_ratio = TurnRightCorner(MAXSPEED=MAX_SPEED)
            if pos == BLANK_SIGNAL:
                g -=g
                e = limit+1
                d = a
                a -= a
                intersectiondirect -= intersectiondirect
                fulllineTime-=fulllineTime

    #----------------------------------------------------------

    #FINISH STOP
    if filted == 0b00000000:
        c+=1
    if filted != 0b00000000:
        c = 0

    if c >= 10 and c < 100:
        left_ratio, right_ratio = 12/MAX_SPEED, 12/MAX_SPEED
    elif c >= 100:
        left_ratio, right_ratio = 0,0
    #-------------------------------------------------------
    #CORNER
    if d == LEFT:
            
        if e <= limit:
            left_ratio, right_ratio = 10/MAX_SPEED, 10/MAX_SPEED
        else:
            left_ratio, right_ratio = TurnLeftCorner(MAXSPEED=MAX_SPEED)
            if pos == MID:
                t = t + 1
                # left_ratio, right_ratio = 0,0
                d -= d
                e-=e
                a-=a
                out_construction-=out_construction

            
    if d == RIGHT:
            
        if e <= limit:
            left_ratio, right_ratio = 10/MAX_SPEED, 10/MAX_SPEED
        else:
            left_ratio, right_ratio = TurnRightCorner(MAXSPEED=MAX_SPEED)
            if pos == MID:
                a-=a
                t =t+1
                # left_ratio, right_ratio = 0,0
                d -= d
                e-=e
                out_construction-=out_construction
    if pos == MID:
        e -= e
#-----------------------------------------------------------------------------

    #CONSTRUCTION
    if distance < 700 and pos == BLANK_SIGNAL:
        if intersectiondirect == LEFT: intersectionConstruction = LEFT
        elif intersectiondirect == RIGHT: intersectionConstruction = RIGHT
        
        
    if intersectionConstruction!= 0: 
        # intersectiondirect-=intersectiondirect
        s=30
        corner=20
        stop_time = 10
        ss=60
        if intersectionConstruction == LEFT:
            time += 1
            if time <= i: left_ratio, right_ratio = 0,0
            elif time > i and time <= ii: left_ratio, right_ratio=-s/MAX_SPEED,-s/MAX_SPEED
            elif time > ii and time <= iii: left_ratio, right_ratio = 0,0
            elif time > iii and time <= iiii: left_ratio, right_ratio = -corner/MAX_SPEED, corner/MAX_SPEED
            elif time > iiii and time <= iiii +stop_time: left_ratio,right_ratio = 0,0
            else:
                left_ratio, right_ratio = ss/MAX_SPEED, ss/MAX_SPEED
                if pos !=BLANK_SIGNAL:
                    
                    intersectionConstruction-=intersectionConstruction
                    intersectiondirect-=intersectiondirect
                    time-=time    
                    a-=a
                    e=0
        elif intersectionConstruction==RIGHT:
            
            time += 1
            
            if time <= i: left_ratio, right_ratio = 0,0
            elif time > i and time <= ii: left_ratio, right_ratio=-s/MAX_SPEED,-s/MAX_SPEED
            elif time > ii and time <= iii: left_ratio, right_ratio = 0,0
            elif time > iii and time <= iiii: left_ratio, right_ratio = corner/MAX_SPEED, -corner/MAX_SPEED
            elif time > iiii and time <= iiii +stop_time: left_ratio,right_ratio = 0,0
            else:
                left_ratio, right_ratio = ss/MAX_SPEED, ss/MAX_SPEED
                if pos != BLANK_SIGNAL:
                    
                    intersectionConstruction-=intersectionConstruction
                    intersectiondirect-=intersectiondirect
                    time-=time
                    e=0
                    a-=a
    if out_construction==RIGHT:
        if pos == FULL_SIGNAL: left_ratio, right_ratio=s/MAX_SPEED,s/MAX_SPEED
        else:
            d=RIGHT
    if out_construction==LEFT:
        if pos == FULL_SIGNAL: left_ratio, right_ratio=s/MAX_SPEED,s/MAX_SPEED
        else:
            d=LEFT
        # out_construction-=out_construction
                
#--------------------------------------------

    
    if t >0:
        t_ +=1
    if t_ < limitStop and t_ != 0:
        left_ratio, right_ratio = 0,0
    else:
        if t_!= 0:
            t -= t
            t_-=t_

    #BRIDGE
    if filted == 0b00000000 and preFilted != 0b00000000:
        fulllineTime += 1
    else:
        fulllineTime += 0
    if fulllineTime >=3:
        if pos != FULL_SIGNAL: delta +=1
        else: delta -= delta
    if fulllineTime >= 3:
        k = 230
        kk = 330
        if pos == FULL_SIGNAL: left_ratio, right_ratio = GoStraight(filted=0b11100111)
        timeOnBridge+=1
        intersectiondirect-=intersectiondirect
        a-=a
        MAX_SPEED = 100
        # print("time:",timeOnBridge)
        if delta < 10:
            # print("Slow")
            if MAX_SPEED >= 80 and MAX_SPEED <= 90: left_ratio, right_ratio = 50/MAX_SPEED, 50/MAX_SPEED

            elif MAX_SPEED > 90: left_ratio, right_ratio = 20/MAX_SPEED, 20/MAX_SPEED
            if pos == BLANK_SIGNAL and timeOnBridge > 530:
                left_ratio, right_ratio = 30/MAX_SPEED, 30/MAX_SPEED
                timeOnBridge-=timeOnBridge
                fulllineTime-=fulllineTime
                delta -= delta
        # if timeOnBridge >0 and timeOnBridge <= k: MAX_SPEED = 99
        # elif timeOnBridge > k and timeOnBridge <= kk: MAX_SPEED=50
        # else: MAX_SPEED = 99
        # elif timeOnBridge> 270 and timeOnBridge <= 400: MAX_SPEED=firstConnection
        # elif timeOnBridge > 400 and timeOnBridge<=800: MAX_SPEED = straightBridge
        # elif timeOnBridge>800 and timeOnBridge<= 830: MAX_SPEED = secondConnection
        # else: MAX_SPEED = downBridge
    # if fulllineTime > 3: 
    #     a-=a
    #     intersectiondirect-=intersectiondirect
    # if fulllineTime == 6:
    #     if pos == MID: 
    #         timeOnBridge-=timeOnBridge
    #         fulllineTime-=fulllineTime

    #ROUNDABOUT HAVING BLOCK
    if distance <= 850 and intersectiondirect==ROUNDABOUT: intersectiondirect=ROUNDABOUTHAVINGBLOCK
    if intersectiondirect==ROUNDABOUTHAVINGBLOCK:
        if pos==BLANK_SIGNAL:
            blockStep+=1
            if blockStep>0 and blockStep <=10:
                left_ratio,right_ratio = 0,0

            elif blockStep>10 and blockStep <= 85:
                left_ratio,right_ratio=45/MAX_SPEED,30/MAX_SPEED
            else:
                left_ratio,right_ratio = 28/MAX_SPEED,38/MAX_SPEED
        if blockStep>85 and pos!=BLANK_SIGNAL:
            intersectiondirect-=intersectiondirect
            a=3

    # print(timeOnBridge, fulllineTime)
    # print(delta)
    # print(MAX_SPEED)
    # print(left_ratio, right_ratio)
    lm.setVelocity(left_ratio * MAX_SPEED)  # set vận tốc cho bánh xe trái
    rm.setVelocity(right_ratio * MAX_SPEED) # set vận tốc cho bánh xe phải
    preFilted = filted

    
pass


