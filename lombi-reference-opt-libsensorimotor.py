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
import argparse, os, pprint, time
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

# display configuration
wScreen = 900
hScreen = 800

# color defaults
lamp_col_default = (255,203,125)
lamp_col_excited = (203,255,255)


# helper function to print a vector
def print_vec(data):
    print(''.join('{0: .3f} '.format(k) for k in data))

# helper function to generate sawtooth signal
def sawtooth(i):
    return min(255,abs(i%511 - 255))

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

def pass_1(lamps):
    """pass 1

    legacy / helper function with mamoun original lombi simulator code
    """
    # get mouse position tuple (x, y)
    pos = pygame.mouse.get_pos()
    # print(f'    while loop mouse pos {pos}')
    
    # get line coords from base lamp and mouse
    line = [(lamps[0].x,lamps[0].y), pos]
    # print(f'    while loop line {line}')
    
    # set position of lamp to mouse pos
    lamps[2].set_position(pos)
    
    # ask lamp for distance to objects
    # lamps[0].distance((lamps[2].x, lamps[2].y))
    d_ = lamps[0].distance(lamps[2])
    # print(f'    while loop dist {d_}')
        
    # check distance threshold
    if d_ <= 200.0:
        lamps[0].color = lamp_col_excited
    else:
        lamps[0].color = lamp_col_default

    # print(f'    while loop line {line}')
    return (lamps, line)

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
    
    # init lamp objects
    lamps = [
        lamp(300, 150, 32, lamp_col_default), # the lamp
        lamp(400, 400, 32, (30, 234, 34)), # random object / lombi smnode
        lamp(150, 150, 32, (200, 34, 34)), # moving person / moving obj
    ]
    print(f'    {__name__} lamps {pprint.pformat(lamps)}')    

    # prepare
    running = True

    # enter main loop: lombi sensorimotor loop
    while running and cord.running():

        # run mamoun legacy code
        lamps, line = pass_1(lamps)

        # daylight brightness simulator
        t = clock()
        D = math.sin(t*T*2*math.pi)
        # D = abs(D)
        D = (D + 1)/2

        # set lamp object brightness via its gain
        lamps[1].gain = D
        print(f'    D = {D}')

        # construct low-level motor message
        f = int(D * 255) # scale daylight value to 8 bit and make integer
        # motor message is list w/ seven items: unk, unk, unk, unk, r, g, b)
        mot = [0,0,255, 255, 255-f, f, 0] # esc, servopos, light
        print(f'    sending mot {mot}')
        # for each smnode on the cord / bus
        for b in range(cord.number_of_motors):
            # send motor message
            cord.set_raw_data_send(b, mot)
            # read sensor message
            x = cord.get_raw_data_recv(0, 11)
            print(f'    sm reply {x}')
            # sleep(0.01) # todo replace by framesync

        # graphics update
        redrawWindow(win, lamps, line)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        # loop timer
        pygame.time.wait(1000//25)

    # quit event and teardown pygame
    pygame.quit()

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
