import argparse, time
from pprint import pformat
import pygame
import math
import os
import RPi.GPIO as GPIO
import random
import numpy

from src.sensorimotor import Sensorimotor
from time import sleep

wScreen = 900
hScreen = 800
#git hallo

lamp_col_default = (255,203,125)
lamp_col_excited = (203,255,255)

def print_vec(data):
    print(''.join('{0: .3f} '.format(k) for k in data))


def sawtooth(i):
    return min(255,abs(i%511 - 255))

class lamp(object):
    def __init__(self,x,y,radius,color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color  = color
        self.gain  = 1.0
      
    @staticmethod    
    def lamppath (stratx, strarty, power, ang, time):
      pass
    
    def set_position(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def draw(self, win):
        color_ = tuple([_ * self.gain for _ in self.color])
        # print(f'    lamp.draw color_ {color_} gain {self.gain}')
        pygame.draw.circle(win, (125,150,150), (self.x,self.y), self.radius)
        pygame.draw.circle(win, color_, (self.x,self.y), self.radius - 5)
        #should be moving object or animate?
        
    def distance(self, pos):
        d_x = self.x - pos.x
        d_y = self.y - pos.y
        # compute euclidean
        distance = math.sqrt ((d_x)**2 + (d_y)**2)
        return distance
        
    def lmb_range(self,radius):
        r_x = self.x
        r_y = self.y
        # self_range = (int)*((radius))**2
        self_range = int(radius**2)
        print(f'lmb_range self.distance {self.distance} self_range {self_range}')
        # print value
        #
        # print 'self.distance'
        # distance > range
        
#         if self.distance > self_range:
#             # update lamp color self.color ( white )
#             pass
#         else self.color ==(0,0,0):
#             pass
#         if self.distance < self_range:
#             pass
#         else self.color == ( 255,255,255):
#             pass
        
class person (object):
    def __init__(self, pos):
        p_x = pos.x
        p_y = pos.y
    
    @staticmethod    
    def lamppath (stratx, strarty, power, ang, time):
      pass   
        
         #range will be the distance betwen lamp1 and lamp2 /person 1
    #def range (self, value):
        #r_x = math.sqrt ((lamp1_d_x)**2 + (lamp2_d_y)**2) 

def redrawWindow(lamps, line):
    win.fill((160,70,10))
    for lamp_i in lamps:
        lamp_i.draw(win)
#     lamp1.draw(win)
#     lamp2.draw(win)
        
    pygame.draw.line(win, (10,10,255), line[0], line[1])
        
    #update
    pygame.display.update()


def main(args, win):
    print(f'{__name__} {lamp}')
    lamps = [
        # the lamp
        lamp(300, 150, 32, lamp_col_default),
        # random object
        lamp(400, 400, 32, (30, 234, 34)),
        # person / moving obj
        lamp(150, 150, 32, (200, 34, 34)),
    ]
    print(f'{__name__} {lamps}')

    # print the value of distance
    # if distance 

    running = True
    while running:
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
        redrawWindow(lamps, line)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.time.wait(1000//25)

    pygame.quit()

def pass_1(lamps):
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
    return time.time()
    
def main_lischt(args, win):
    """main lischt

    simple lombi setup:
    - internal clock
    - external clock sensor
    - clock estimate
    - led motor from inverted clock

    two configurations:
    1. simulation pygame output
    2. single sensorimotor node hex-tile output
    """
    print(f'main_lischt args {args}')

    cord = Sensorimotor(number_of_motors=6, verbose=False, update_rate_Hz = 100)

    try:
        # checking for motors
        N = cord.ping()
        print("Found {0} sensorimotors.".format(N))
        sleep(0.25)

        # starting motorcord
        cord.start()
        i = 0
    except:
        # Script crashed?
        print("\rException thrown, stopping cord.")
        cord.stop()
        raise
    
    # T = 0.5
    T = args.clock_freq
    # init lamp object
    lamps = [
        lamp(300, 150, 32, lamp_col_default), # the lamp
        lamp(400, 400, 32, (30, 234, 34)), # random object
        lamp(150, 150, 32, (200, 34, 34)), # person / moving obj
    ]
    print(f'    {__name__} lamps {pformat(lamps)}')    
    
    running = True

    # enter main loop
    while running and cord.running():
        
        lamps, line = pass_1(lamps)

        # random object daylight pulse
        t = clock()
        D = math.sin(t*T*2*math.pi)
        # D = abs(D)
        D = (D + 1)/2
        
        lamps[1].gain = D
        
        print(f'    D = {D}')

        # tmp = lamps[1].color
        # tmp1 = tuple([_ * D for _ in tmp])
        # lamps[1].color = tmp1

        f = int(D * 255) # lamps[1].color[]
        mot = [0,0,f] # esc, servopos, light
        print(f'    sending mot {mot}')
        for b in range(cord.number_of_motors):
            cord.set_raw_data_send(b, mot)

        x = cord.get_raw_data_recv(0, 11)
        print(f'    sm reply {x}')
        # sleep(0.01) # todo replace by framesync
        
        redrawWindow(lamps, line)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        # loop[ timer
        pygame.time.wait(1000//25)

    # quit event and teardown pygame
    pygame.quit()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clock-freq', type=float, default=0.5,
                        help='Internal clock frequency [0.5Hz]')
    parser.add_argument('-m', '--mode', type=str, default='main', help='Program mode [main]')
    args = parser.parse_args()

    win = pygame.display.set_mode((wScreen, hScreen))
    
    if args.mode == 'main':
        main(args, win)
    elif args.mode == 'lischt':
        main_lischt(args, win)
