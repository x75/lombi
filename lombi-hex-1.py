"""lombi reference with sensorimotor

lombi is a lamp robot. the script is designed to talk to sensorimotor
nodes and represents the sensorimotor loop of this robot.

robot body is an smnode with
- motors: LED, (props)
- sensors: brightness x 2, distance, capsense

the smnode is a PCB w/ Atmel micro-controller. several smnodes can
communicate via a serial bus

Main dependency beside the standard stuff is libsensorimotor

To install it, git clone it from github.com/ku3i and then tell Python
about it by saying (copy & paste into a Terminal)

```bash
export PYTHONPATH=/home/pi/work/libsensorimotor/py:$PYTHONPATH
```

We are using pygame for display and events. To run it on a headless
raspi you need to use the dummy display driver for the SDL library by
saying (copy & paste into a Terminal)

```bash
export SDL_VIDEODRIVER=dummy
```


"""
# standard imports
import argparse, os, pprint, time, copy
# math / numerical imports
import math, random
# import numpy as np

# import pygame game engine for (internal) simulation
import pygame

# import raspi hardware driver
import RPi.GPIO as GPIO

# import jetpack hardware driver for sensorimotor / smnode
#
from src.sensorimotor import Sensorimotor

#########################################################
# lombi configuration

TWOPI = 2*math.pi

# display configuration
wScreen = 900
hScreen = 800

# color defaults
lamp_col_default = (255,203,125)
lamp_col_excited = (203,255,255)

loopfreq_default = 25
looprate_default = 1/loopfreq_default
looprate_default_ms = int(looprate_default * 1000)

# helper function to print a vector
def print_vec(data):
    print(''.join('{0: .3f} '.format(k) for k in data))

# helper function to generate sawtooth signal
def sawtooth(i):
    return min(255,abs(i%511 - 255))

def get_random_color(levels=False):
    if levels:
        levels = range(32,256,32)
        return tuple(random.choice(levels) for _ in range(3))
    else:
        return tuple(random.randint(0, 255) for _ in range(3))

# lamp class definition
class lamp(object):
    """lamp

    lamp has attributes:
    - position (x,y)
    - radius
    - color (r, g, b)
    - gain

    These are needed for the simulation.

    On the hardware only color and gain are used.
    """
    def __init__(self, x=0, y=0,
                 radius=10.0, color=(255, 128, 0),
                 gain=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color  = color
        self.gain  = gain

    def set_position(self, pos):
        """set position of lamp
        """
        # Copy values from the tuple into each scalar coordinate
        self.x = pos[0]
        self.y = pos[1]

    def draw(self, win):
        """draw lamp

        Requires pygame win argument to draw in.
        """
        # apply gain to color tuple
        color_ = tuple([_ * self.gain for _ in self.color])
        # print(f'    lamp.draw color_ {color_} gain {self.gain}')

        # draw lamp as a circle
        pygame.draw.circle(win, color_, (self.x,self.y), self.radius - 5)
        # with a border
        pygame.draw.circle(win, (125,150,150), (self.x,self.y), self.radius)

    def distance(self, pos):
        """get distance of lamp to another object at pos
        """
        # get coordinates
        d_x = self.x - pos.x
        d_y = self.y - pos.y
        # compute euclidean distance
        distance = math.sqrt ((d_x)**2 + (d_y)**2)
        return distance

    def lmb_range(self,radius):
        """get range defined as squared radius
        """
        r_x = self.x
        r_y = self.y
        # self_range = (int)*((radius))**2
        self_range = int(radius**2)
        print(f'lmb_range self.distance {self.distance} self_range {self_range}')

# main redraw function
def redrawWindow(win, lamps, line):
    """redraw pygame SDL window

    Requires list / array of lamp objects and a line object
    """
    # fill background color
    win.fill((160,70,10))
    # for each lamp object
    for lamp_i in lamps:
        # draw the lamp
        lamp_i.draw(win)

    # draw a connecting line for debugging distance based lamp
    # behavior
    pygame.draw.line(win, (10,10,255), line[0], line[1])

    # update display
    pygame.display.update()

def clock():
    """clock model

    most simple internal clock model

    returns system time / counter
    """
    return time.time()

def cord_init():
    # create sensorimotor communication bus
    cord = Sensorimotor(
        number_of_motors=6,   # how many motors
        verbose=False,        # print debug info
        update_rate_Hz = 100) # low-level update frequency

    try:
        # checking for motors
        N = cord.ping()
        print("Found {0} sensorimotors.".format(N))
        time.sleep(0.25)

        # starting motorcord
        cord.start()
        i = 0
    except:
        # Script crashed?
        print("\rException thrown, stopping cord.")
        cord.stop()
        raise
    return cord

def get_frequency_modulator(t):
    T_1 = math.cos(t*0.05*TWOPI) + 1 * 0.125
    T_2 = math.cos(t*0.057*TWOPI) + 1 * 0.125
    T_3 = math.cos(t*0.0478*TWOPI) + 1 * 0.125
    T_ = (T_1 + T_2 + T_3) * 0.33
    # T_ = math.pow
    T_ = math.pow(T_, 2) * 0.1
    T_ = round(T_, 2)
    # print(f'    T_ = {T_}')
    return T_

def get_color_modulator(b, D_phi, D_, looprate_default, T, T_):
    phase_lag = b * (1/6)
    # D_[b] = math.pow(math.sin(t*T*TWOPI + T_ + phase_lag), 2)
    # basic_ = math.sin(t*T*TWOPI + T_ + phase_lag)
    phase_incr = looprate_default * T # * TWOPI
    D_phi[b] = D_phi[b] + phase_incr + T_
    basic_ = math.sin((D_phi[b] + phase_lag) * TWOPI)
    D_[b] = math.pow(basic_, 1)
    D_[b] = math.tanh(D_[b] * 3)
    D_[b] = (D_[b] + 1)/2
    D_[b] = round(D_[b], 2)
    return (D_phi, D_)

def main_lischt(args, win):
    """main lischt

    lombi sensorimotor setup v0:
    - internal clock
    - external clock sensor
    - clock estimate
    - LED motor from inverted clock

    Two runtime situations
    1. Simulation only with pygame output
    2. Sensorimotor bus with real hardware output on smnode
    """
    print(f'main_lischt args {args}')

    # create / initialize sensorimotor cord
    if args.hardware:
        cord = cord_init()
    else:
        cord = object()
        cord.running = lambda: True

    # internal clock frequency
    T = args.clock_freq

    lamp1_color = get_random_color()

    # init lamp objects
    lamps = [
        lamp(300, 150, 32, lamp_col_default), # the lamp
        lamp(400, 400, 32, lamp1_color), # random object / lombi smnode
        lamp(150, 150, 32, (200, 34, 34)), # moving person / moving obj
    ]
    print(f'    {__name__} lamps {pprint.pformat(lamps)}')

    # prepare
    running = True

    # one state per channel: red
    D_r = [0. for _ in range(cord.number_of_motors)]
    D_phi_r = [0. for _ in range(cord.number_of_motors)]
    # one state per channel: green
    D_g = [0. for _ in range(cord.number_of_motors)]
    D_phi_g = [0. for _ in range(cord.number_of_motors)]
    # one state per channel: blue
    D_b = [0. for _ in range(cord.number_of_motors)]
    D_phi_b = [0. for _ in range(cord.number_of_motors)]

    loopcnt = 0
    motorlen = 7
    sensorlen = 11
    # motor matrix 6 x 7
    # [
    #   [0, 0, 255, 255, R_0, G_0, B_0],
    #   [0, 0, 255, 255, R_1, G_1, B_1],
    #   [...]
    #]
    motors = [[0 for _ in range(motorlen)] for _1 in range(cord.number_of_motors)]
    sensors = [[0 for _ in range(sensorlen)] for _1 in range(cord.number_of_motors)]
    s_bright_1 = 5
    s_bright_2 = 6
    s_range_1 = 10

    sensor3 = [0 for _ in range(11)]

    # enter main loop: lombi sensorimotor loop
    while running and cord.running():


        # run mamoun legacy code
        # lamps, line = pass_1(lamps)

        # daylight brightness simulator
        t = clock()

        # set lamp object brightness via its gain
        # lamps[1].gain = D_r[0]
        # print(f'    D_r = {D_r}')
        gain1 = 0.5
        # for each smnode on the cord / bus
        for smnode_id in range(cord.number_of_motors):
            # work here
            c_red = 0 # int()
            c_green = 0
            c_blue = int(max(60, sensors[4][s_range_1])-60)
            # motor message is list w/ seven items: unk, unk, unk, unk, r, g, b)
            # mot = [0,0,255, 255, abs(63-f), f, abs(191-f)//2] # esc, servopos, light
            # mot = [0,0,255, 255, int(f), 0, 0] # esc, servopos, light
            motor_message = [0, 0, 255, 225, c_red, c_green, c_blue] # esc, servopos, light

            print(f'motor_message {smnode_id} {motor_message}')
            # save the motor values for smnode_id
            motors[smnode_id] = copy.copy(motor_message)
            # print(f'    sm sending motors {mot}')
            # send motor message
            cord.set_raw_data_send(smnode_id, motor_message)
            # read sensor message
            sensor = cord.get_raw_data_recv(smnode_id, sensorlen)

            # save sensor values for smnode_id
            sensors[smnode_id] = copy.copy(sensor)
            # if smnode_id == 4:
            #     print(sensor)
            # if b == 3:
            #     sensor3 = sensor
            # print(f'    sm reply sensor {sensor3[5]} {sensor3[6]}')
            # brightness sensors are 5 and 6
            # print(f'    sm receive sensors brightness {x[5]} {x[6]}')
            # sleep(0.01) # todo replace by framesync

        if loopcnt % 100 == 0:
            if random.uniform(0, 1) > 0.8:
                lamps[1].color = get_random_color()
                print(f'    new color = {lamps[1].color}')


        # graphics update
        # redrawWindow(win, lamps, line)
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # stopping motor cord
                    running = cord_close(cord)

            # loop timer
            pygame.time.wait(looprate_default_ms)
            loopcnt +=1

        except (KeyboardInterrupt, SystemExit):
            # stopping motor cord
            running = cord_close(cord)

    # quit event and teardown pygame
    pygame.quit()

def cord_close(cord):
    print(f"    cord_close, stopping motors")
    cord.stop()
    return False

# main dummy
def main(args): pass

# ...
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clock-freq', type=float, default=0.10,
                        help='Internal clock frequency [0.10Hz]')
    parser.add_argument('-m', '--mode', type=str, default='lischt',
                        help='Program mode [lischt]')
    parser.add_argument('-hw', '--hardware', default='False',
                        action='store_true', help='Have hardware? [False]')
    args = parser.parse_args()

    win = pygame.display.set_mode((wScreen, hScreen))

    if args.mode == 'main':
        main(args, win)
    elif args.mode == 'lischt':
        main_lischt(args, win)

# opt+mamoun was here
