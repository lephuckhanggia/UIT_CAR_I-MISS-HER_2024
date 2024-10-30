#Thang
from controller import Robot
from controller import Motor
from controller import DistanceSensor
from controller import Camera
from controller import LED
from controller import Supervisor
import math

# ---------------Khởi tạo thông tin robot---------------#
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

# ---------------Phần code code set up---------------#

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
    if (robot.getTime() - initTime) * 1000 % 3000 >= 2000:
        leds[1].set(1)
    return


# -------------------Define-------------------#
time = 0
threshold = [300, 300, 300, 300, 300, 300, 300, 300]
NOP = 0.1
a = 0
b = 0
c = 0
d = 0
e = 0
f = 0
g = 0
h = 0
i = 0
j = 0
l = 0
m = 0
n = 0
r = 0
s = 0
t = 0
u = 0
v = 0
w = 0
x = 0
y = 0
z = 0
ab = 0
bc = 0
k = 0
o = 0

# ----------Speed----------#
speed_max = 68.5
speed_extra_min = 20
speed_min = 57
speed_extra_max = 85
speed_min1 = 18
speed_min2 = 25
speed_min3 = 40
speed_cua = 20
speed_cua_nhe = 10
speed_cua_sieu_nhe = 5
time_cheo = 44

# ----------Signal----------#

chinh_giua = 0
lech_phai1 = 1
lech_trai1 = -1
lech_phai2 = 2
lech_trai2 = -3
lech_phai3 = 4
lech_trai3 = -4
lech_phai4 = -5
lech_trai4 = 5
re_phai = -6
re_trai = 6
full_trang = 7
full_den = -8


# ----------Def_motor----------#

def di_thang():
    lm.setVelocity(speed_max)
    rm.setVelocity(speed_max)


def di_thang_cham():
    lm.setVelocity(speed_min)
    rm.setVelocity(speed_min)


def di_thang_sieu_cham():
    lm.setVelocity(speed_extra_min)
    rm.setVelocity(speed_extra_min)


def di_thang_nhanh():
    lm.setVelocity(speed_extra_max)
    rm.setVelocity(speed_extra_max)


def chinh_phai1():
    lm.setVelocity(speed_max)
    rm.setVelocity(speed_max - speed_min1)


def chinh_trai1():
    lm.setVelocity(speed_max - speed_min1)
    rm.setVelocity(speed_max)


def chinh_phai2():
    lm.setVelocity(speed_max)
    rm.setVelocity(speed_max - speed_min2)


def chinh_trai2():
    lm.setVelocity(speed_max - speed_min2)
    rm.setVelocity(speed_max)


def chinh_phai3():
    lm.setVelocity(speed_max)
    rm.setVelocity(speed_max - speed_min3)


def chinh_trai3():
    lm.setVelocity(speed_max - speed_min3)
    rm.setVelocity(speed_max)


def chinh_phai4():
    lm.setVelocity(speed_max)
    rm.setVelocity(0)


def chinh_trai4():
    lm.setVelocity(0)
    rm.setVelocity(speed_max)


def dung_yen():
    lm.setVelocity(0)
    rm.setVelocity(0)


# ----------Turn----------#

def re_phai():
    lm.setVelocity(speed_cua)
    rm.setVelocity(speed_cua - speed_cua * 2)


def re_trai():
    lm.setVelocity(speed_cua - speed_cua * 2)
    rm.setVelocity(speed_cua)


def re_phai_nhe():
    lm.setVelocity(speed_cua_nhe)
    rm.setVelocity(speed_cua_nhe - speed_cua_nhe * 2)


def re_trai_nhe():
    lm.setVelocity(speed_cua_nhe - speed_cua_nhe * 2)
    rm.setVelocity(speed_cua_nhe)


def re_phai_sieu_nhe():
    lm.setVelocity(speed_cua_sieu_nhe)
    rm.setVelocity(speed_cua_sieu_nhe - speed_cua_sieu_nhe * 2)


def re_trai_sieu_nhe():
    lm.setVelocity(speed_cua_sieu_nhe - speed_cua_sieu_nhe * 2)
    rm.setVelocity(speed_cua_sieu_nhe)


# ----------Def_sensor----------#
def ReadSensors():
    gsValues = []
    filted = 0x00
    for i in range(NB_GROUND_SENS):
        gsValues.append(gs[i].getValue())
        if gsValues[i] < threshold[i]:
            filted |= (0x01 << (NB_GROUND_SENS - i - 1))
    return filted


# ----------Get_signal----------#

def DeterminePosition(filted):
    if filted == 0b00011000:
        return chinh_giua

    elif filted == 0b00010000:
        return lech_phai1
    elif filted == 0b00001000:
        return lech_trai1

    elif filted in [0b00110000]:
        return lech_phai2
    elif filted in [0b00001100]:
        return lech_trai2

    elif filted in [0b01100000, 0b00100000]:
        return lech_phai3
    elif filted in [0b00000110, 0b00000100]:
        return lech_trai3

    elif filted in [0b11000000, 0b10000000, 0b01000000]:
        return lech_phai4
    elif filted in [0b00000001, 0b00000010, 0b00000011]:
        return lech_trai4

    elif filted in [0b00001110, 0b00011111, 0b00001111, 0b00000111]:
        return re_phai
    elif filted in [0b01110000, 0b11111000, 0b11110000, 0b11100000]:
        return re_trai

    elif filted in [0b11111111, 0b01111110, 0b01111111, 0b11111110]:
        return full_trang
    elif filted in [0b00000000]:
        return full_den

    return NOP


# -------------Main_code-------------#

while robot.step(TIME_STEP) != -1:
    time = time + 1
    filted = ReadSensors()
    global ds_value
    dis = ds.getValue()
    pos = DeterminePosition(filted)
    # print(" ")
    # print(dis)
    # print('Pos: ' + str(format(filted, '08b')), 'Status:', pos, '   Var:', ' a:', a, ' b:', b, ' c:', c, ' d:', d,
    #     ' e:', e, ' f:', f, ' g:', g, ' h:', h, ' i:', i, ' j:', j, ' l:', l, ' m:', m, ' n:', n, ' r:', r, ' s:', s, ' t:', t, ' u:', u, ' v:', v, ' w:', w, ' x:', x, ' y:', y, ' z:', z, ' ab:',
    #    ab,' bc:',bc,' o:',o,  end='   ')

    if pos == chinh_giua and c == 0 and f == 0 and m == 0 and n == 0 and s == 0 and u == 0 and d == 0 and e == 0 and k == 0:
        di_thang()
        a = 0
        b = 0
        x = 0
        y = 0
        z = 0
        ab = 0
        bc = 0
        time = 0
        g = 0
        w = 0
    if pos == chinh_giua and c == 0 and f == 0 and m == 0 and n == 0 and s == 0 and u == 0 and dis == 1000 and d == 0 and e == 0 and k != 0:
        di_thang_cham()
        a = 0
        b = 0
        x = 0
        y = 0
        z = 0
        ab = 0
        bc = 0
        time = 0
        g = 0
        w = 0
    if pos == chinh_giua and d != 0:
        di_thang_cham()
        a = 0
        b = 0
        time = 0
        g = 0
        x = 0
        y = 0
        z = 0
        ab = 0
        bc = 0
        w = 0
    if pos == chinh_giua and e != 0:
        di_thang_cham()
        a = 0
        b = 0
        time = 0
        g = 0
        x = 0
        y = 0
        z = 0
        ab = 0
        bc = 0
        w = 0
    elif pos == chinh_giua and c != 0:
        re_phai()
    elif pos == chinh_giua and f != 0:
        re_trai()
    elif pos == chinh_giua and i != 0 and h != 0:
        re_phai()
    elif pos == chinh_giua and s != 0:
        s = 0
    elif pos == chinh_giua and u != 0:
        re_phai()
    elif pos == chinh_giua and m != 0:
        re_phai()
        g = 0
    elif pos == chinh_giua and n != 0:
        re_trai()
        g = 0


    elif pos == lech_phai1 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and w == 0 and v == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_trai1()
    elif pos == lech_trai1 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and w == 0 and v == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_phai1()
    elif pos == lech_phai1 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_trai1 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_phai1 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_trai1 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_phai1 and h != 0 and i != 0:
        re_phai()
    elif pos == lech_trai1 and h != 0 and i != 0:
        re_phai_sieu_nhe()
    elif pos == lech_phai1 and m != 0:
        re_phai()
    elif pos == lech_trai1 and m != 0:
        re_phai()
    elif pos == lech_phai1 and n != 0:
        re_trai()
    elif pos == lech_trai1 and n != 0:
        re_trai()
    elif pos == lech_phai1 and s != 0:
        re_trai()
    elif pos == lech_trai1 and s != 0:
        re_trai()
    elif pos == lech_phai1 and u != 0:
        re_phai()
    elif pos == lech_trai1 and u != 0:
        re_phai()
    elif pos == lech_phai1 and v != 0:
        re_trai()
    elif pos == lech_trai1 and v != 0:
        re_trai()
    elif pos == lech_phai1 and u != 0:
        re_phai()
    elif pos == lech_trai1 and u != 0:
        re_phai()


    elif pos == lech_phai1 and y != 0:
        re_trai_sieu_nhe()
    elif pos == lech_trai1 and y != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai1 and x != 0:
        re_phai_sieu_nhe()
    elif pos == lech_trai1 and x != 0:
        re_phai_sieu_nhe()
    elif pos == lech_trai1 and w != 0:
        re_phai_sieu_nhe()
    elif pos == lech_phai1 and bc != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai1 and z != 0:
        re_trai_sieu_nhe()
    elif pos == lech_trai1 and z != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai1 and ab != 0:
        re_phai_sieu_nhe()
    elif pos == lech_trai1 and ab != 0:
        re_phai_sieu_nhe()



    elif pos == lech_phai2 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and v == 0 and w == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_trai2()
    elif pos == lech_trai2 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and v == 0 and w == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_phai2()
    elif pos == lech_phai2 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_trai2 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_phai2 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_trai2 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_phai2 and h != 0 and i != 0:
        re_phai()
    elif pos == lech_trai2 and h != 0 and i != 0:
        re_phai_nhe()
    elif pos == lech_phai2 and m != 0:
        re_phai()
    elif pos == lech_trai2 and m != 0:
        re_phai()
    elif pos == lech_phai2 and n != 0:
        re_trai()
    elif pos == lech_trai2 and n != 0:
        re_trai()
    elif pos == lech_phai2 and s != 0:
        re_trai()
    elif pos == lech_trai2 and s != 0:
        re_trai()
    elif pos == lech_phai2 and v != 0:
        re_trai()
    elif pos == lech_trai2 and v != 0:
        re_trai()
    elif pos == lech_phai2 and u != 0:
        re_phai()
    elif pos == lech_trai2 and u != 0:
        re_phai()
    elif pos == lech_phai2 and y != 0:
        re_trai_sieu_nhe()
    elif pos == lech_trai2 and y != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai2 and x != 0:
        re_phai_sieu_nhe()
    elif pos == lech_trai2 and x != 0:
        re_phai_sieu_nhe()

    elif pos == lech_phai2 and u != 0:
        re_phai()
    elif pos == lech_trai2 and u != 0:
        re_phai()




    elif pos == lech_trai2 and w != 0:
        re_phai_sieu_nhe()
    elif pos == lech_phai2 and bc != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai2 and z != 0:
        re_trai_sieu_nhe()
    elif pos == lech_trai2 and z != 0:
        re_trai_sieu_nhe()
    elif pos == lech_phai2 and ab != 0:
        re_phai_sieu_nhe()
    elif pos == lech_trai2 and ab != 0:
        re_phai_sieu_nhe()




    elif pos == lech_phai3 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and v == 0 and w == 0 and y == 0 and x == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_trai3()
    elif pos == lech_trai3 and c == 0 and f == 0 and i == 0 and m == 0 and n == 0 and s == 0 and u == 0 and v == 0 and w == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and bc == 0:
        chinh_phai3()
    elif pos == lech_phai3 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_trai3 and c != 0 and f == 0:
        re_phai()
    elif pos == lech_phai3 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_trai3 and c == 0 and f != 0:
        re_trai()
    elif pos == lech_phai3 and h != 0 and i != 0:
        re_phai()
    elif pos == lech_trai3 and h != 0 and i != 0:
        re_phai()

    elif pos == lech_phai3 and m != 0:
        re_phai()
    elif pos == lech_trai3 and m != 0:
        re_phai()
    elif pos == lech_phai3 and n != 0:
        re_trai()
    elif pos == lech_trai3 and n != 0:
        re_trai()
    elif pos == lech_phai3 and v != 0:
        re_trai()
    elif pos == lech_trai3 and v != 0:
        re_trai()
    elif pos == lech_phai3 and u != 0:
        re_phai()
    elif pos == lech_trai3 and u != 0:
        re_phai()



    elif pos == lech_phai3 and s != 0:
        re_trai()
    elif pos == lech_trai3 and s != 0:
        re_trai()
    elif pos == lech_phai3 and u != 0:
        re_phai()
    elif pos == lech_trai3 and u != 0:
        re_phai()

    elif pos == lech_phai3 and y != 0:
        re_trai_nhe()
    elif pos == lech_trai3 and y != 0:
        re_trai_nhe()
    elif pos == lech_phai3 and x != 0:
        re_phai_nhe()
    elif pos == lech_trai3 and x != 0:
        re_phai_nhe()
    elif pos == lech_trai3 and w != 0:
        re_phai_nhe()
    elif pos == lech_phai3 and bc != 0:
        re_trai_nhe()

    elif pos == lech_phai3 and z != 0:
        re_trai_nhe()
    elif pos == lech_trai3 and z != 0:
        re_trai_nhe()
    elif pos == lech_phai3 and ab != 0:
        re_phai_nhe()
    elif pos == lech_trai3 and ab != 0:
        re_phai_nhe()



    elif pos == lech_phai4 and c == 0 and i == 0 and m == 0 and n == 0 and u == 0 and f == 0 and y == 0 and x == 0 and bc == 0 and w == 0 and z == 0 and ab == 0 and a == 0 and b == 0 and g == 0:
        chinh_trai4()
        z = z + 1
    elif pos == lech_trai4 and c == 0 and i == 0 and m == 0 and n == 0 and u == 0 and f == 0 and x == 0 and y == 0 and w == 0 and bc == 0 and z == 0 and ab == 0 and a == 0 and b == 0 and g == 0:
        chinh_phai4()
        ab = ab + 1
    elif pos == lech_phai4 and c == 0 and i == 0 and m == 0 and n == 0 and u == 0 and f == 0 and y != 0:
        re_trai_nhe()
    elif pos == lech_trai4 and c == 0 and i == 0 and m == 0 and n == 0 and u == 0 and f == 0 and x != 0:
        re_phai_nhe()

    elif pos == lech_phai4 and c == 0 and i == 0 and m == 0 and n == 0 and u == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and a == 0 and b == 0 and f != 0:
        re_trai_nhe()
        bc = bc + 1
        f = 0
    elif pos == lech_trai4 and f == 0 and i == 0 and m == 0 and n == 0 and u == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and a == 0 and b == 0 and c != 0:
        re_phai_nhe()
        w = w + 1
        c = 0
    elif pos == lech_trai4 and c == 0 and f == 0 and m == 0 and n == 0 and u == 0 and x == 0 and y == 0 and z == 0 and ab == 0 and a == 0 and b == 0 and h != 0 and i != 0:
        re_phai()
        w = w + 1
        i = 0
        h = 0
    elif pos == lech_trai4 and f == 0 and i == 0 and m == 0 and n == 0 and c == 0 and u != 0:
        chinh_phai4()
        u = 0
    elif pos == lech_phai4 and z != 0:
        re_trai_nhe()
    elif pos == lech_trai4 and z != 0:
        re_trai_nhe()
    elif pos == lech_phai4 and ab != 0:
        re_phai_nhe()
    elif pos == lech_trai4 and ab != 0:
        re_phai_nhe()


    elif pos == re_phai and h == 0 and s == 0 and m == 0 and n == 0 and z == 0 and ab == 0:
        dung_yen()
        a = a + 1
        d = d + 1
        j = j + 1
    elif pos == re_trai and h == 0 and s == 0 and m == 0 and n == 0 and z == 0 and ab == 0:
        dung_yen()
        b = b + 1
        e = e + 1
        l = l + 1
    elif filted in [0b00001110, 0b00011111, 0b00001111, 0b00000111, 0b00111110, 0b00011110, 0b00111111, 0b00010111,
                    0b00110111, 0b00111100] and h != 0:
        i = i + 1
    elif filted in [0b00001110, 0b00011111, 0b00001111, 0b00000111, 0b00111110, 0b00011110] and t != 0:
        u = u + 1

    elif pos == full_den and a == 0 and b == 0 and c == 0 and f == 0 and g == 0 and h == 0 and dis == 1000 and r == 0 and u == 0 and z == 0 and ab == 0 and j == 0 and l == 0 and o == 0:
        di_thang_nhanh()
    elif pos == full_den and a == 0 and b == 0 and c == 0 and f == 0 and g == 0 and h == 0 and dis == 1000 and r == 0 and u == 0 and z == 0 and ab == 0 and j == 0 and l == 0 and o != 0:
        di_thang()
    elif pos == full_den and a == 0 and b == 0 and c == 0 and f == 0 and g == 0 and h == 0 and r == 0 and u == 0 and z != 0:
        re_trai()
    elif pos == full_den and a == 0 and b == 0 and c == 0 and f == 0 and g == 0 and h == 0 and r == 0 and u == 0 and ab != 0:
        re_phai()

    elif pos == full_den and a != 0 and c == 0 and f == 0:
        re_phai()
        x = x + 1
        d = 0
        j = 0
    elif pos == full_den and b != 0 and c == 0 and f == 0:
        re_trai()
        y = y + 1
        e = 0
        l = 0
    elif pos == full_den and g != 0 and c == 0 and f == 0 and dis == 1000 and m == 0 and n == 0:
        re_phai()
        h = h + 1
        k = 0
        ab = ab + 1
    elif pos == full_den and dis != 1000 and r == 0 and c == 0 and f == 0 and j == 0 and l == 0 and m == 0 and n == 0 and z == 0 and ab == 0:
        r = r + 1
    elif pos == full_den and r != 0 and time < 24:
        re_phai()
        g = 0
    elif pos == full_den and r != 0 and time >= 24:
        r = 0
        s = s + 1
        t = t + 1
    elif pos == full_den and j != 0 and time > time_cheo:
        a = 0
        d = 0
        j = 0
        m = m + 1
        o = o + 1
    elif pos == full_den and j != 0 and time < time_cheo:
        re_phai()
        a = 0
        d = 0
    elif pos == full_den and l != 0 and time > time_cheo:
        b = 0
        e = 0
        l = 0
        n = n + 1
        o = o + 1
    elif pos == full_den and l != 0 and time < time_cheo:
        re_trai()
        b = 0
        e = 0



    elif pos == full_trang and d == 0 and e == 0 and time < 16 and m == 0 and n == 0:
        di_thang_cham()
        g = g + 1
        k = k + 1
    elif pos == full_trang and d == 0 and e == 0 and time > 16 and m == 0 and n == 0:
        dung_yen()

    elif pos == full_trang and d != 0:
        dung_yen()
        c = c + 1
        d = 0
        j = 0
    elif pos == full_trang and e != 0:
        dung_yen()
        f = f + 1
        e = 0
        l = 0
    elif pos == full_trang and j != 0 and dis != 1000:
        j = 0
    elif pos == full_trang and l != 0 and dis != 1000:
        l = 0
    elif pos == full_trang and m != 0:
        dung_yen()
        z = z + 1
        m = 0
        o = 0
    elif pos == full_trang and n != 0:
        dung_yen()
        ab = ab + 1
        n = 0
        o = 0