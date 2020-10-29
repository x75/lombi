import pygame
import math
import os
import RPi.GPIO as GPIO
import random
import time
import numpy

wScreen = 900
hScreen = 800
#git hallo

win = pygame.display.set_mode((wScreen, hScreen))

class lamp(object):
    def __init__(self,x,y,radius,color):
     self.x = x
     self.y = y
     self.radius = radius
     self.color  = color
     # self.pos = (x, y)
 
    @staticmethod    
    def lamppath (stratx, strarty, power, ang, time):
      pass
    
    def set_position(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def draw(self, win):
        pygame.draw.circle(win, (125,150,150), (self.x,self.y), self.radius)
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius - 5)
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
    
print(f'{__name__} {lamp}')
lamp_col_default = (255,203,125)
lamp_col_excited = (203,255,255)
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
    print(f'    while loop mouse pos {pos}')
    
    # get line coords from base lamp and mouse
    line = [(lamps[0].x,lamps[0].y), pos]
    print(f'    while loop line {line}')
    
    # set position of lamp to mouse pos
    lamps[2].set_position(pos)
    
    # ask lamp for distance to objects
    # lamps[0].distance((lamps[2].x, lamps[2].y))
    d_ = lamps[0].distance(lamps[2])
    print(f'    while loop dist {d_}')
    
    # check distance threshold
    if d_ <= 200.0:
        lamps[0].color = lamp_col_excited
    else:
        lamps[0].color = lamp_col_default

    print(f'    while loop line {line}')
    redrawWindow(lamps, line)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
