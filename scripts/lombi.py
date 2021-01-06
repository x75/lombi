"""lombi reference

lombi is a lamp robot. the script is designed to talk to sensorimotor
nodes and represents the sensorimotor loop of this robot.

robot body is an smnode with
- motors: LED, (props)
- sensors: brightness x 2, distance, capsense

the smnode is a PCB w/ Atmel micro-controller. several smnodes can
communicate via a serial bus

Depends: liblo, libsensorimotor, pygame

TODO
- run osc2sensorimotor

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
from functools import partial

# TODO: make these imports optional
# import pygame game engine for (internal) simulation
import pygame

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

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

if is_raspberrypi():
    # import raspi hardware driver
    import RPi.GPIO as GPIO

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

def smloop_lischt_init(cord):
    return {
        # one state per channel: red
        'D_r': [0. for _ in range(cord.number_of_motors)],
        'D_phi_r': [0. for _ in range(cord.number_of_motors)],
        # one state per channel: green
        'D_g': [0. for _ in range(cord.number_of_motors)],
        'D_phi_g': [0. for _ in range(cord.number_of_motors)],
        # one state per channel: blue
        'D_b': [0. for _ in range(cord.number_of_motors)],
        'D_phi_b': [0. for _ in range(cord.number_of_motors)],
        'lamp1_color': get_random_color(),
        'lamp1': lamp(400, 400, 32, get_random_color()),
    }

def smloop_lischt(smnode_id, loopcnt, cord, **kwargs):
    """smloop lischt

    lombi sensorimotor setup v0:
    - internal clock
    - external clock sensor
    - clock estimate
    - LED motor from inverted clock

    Two runtime situations
    1. Simulation only with pygame output
    2. Sensorimotor bus with real hardware output on smnode
    """
    # print(f'main_lischt args {args}')

    # internal clock frequency
    # T = args.clock_freq
    T = kwargs['clock_freq']
    lamp1_color = kwargs['lamp1_color']
    lamp1 = kwargs['lamp1']


    D_r = kwargs['D_r']
    D_phi_r = kwargs['D_phi_r']
    D_g = kwargs['D_g']
    D_phi_g = kwargs['D_phi_g']
    D_b = kwargs['D_b']
    D_phi_b = kwargs['D_phi_b']
    
    # daylight brightness simulator
    t = clock()

    # frequency modulator
    T_r = get_frequency_modulator(t)
    T_g = get_frequency_modulator(t)
    T_b = get_frequency_modulator(t)
    
    # color modulators
    D_phi_r, D_r = get_color_modulator(smnode_id, D_phi_r, D_r, looprate_default, T, T_r)
    D_phi_g, D_g = get_color_modulator(smnode_id, D_phi_g, D_g, looprate_default, T, T_g)
    D_phi_b, D_b = get_color_modulator(smnode_id, D_phi_b, D_b, looprate_default, T, T_b)
        
    # set lamp object brightness via its gain
    # lamp1.gain = D_r[0]
    # print(f'    D_r = {D_r}')
    gain1 = 0.5
    # for each smnode on the cord / bus
    # for b in range(cord.number_of_motors):
        
    # construct low-level motor message
    # f = int(D_r[smnode_id] * 255) # scale daylight value to 8 bit and make integer
    # f_ = D_r[smnode_id] # scale daylight value to 8 bit and make integer
    # print(f'    f = {f}, color = {lamp1.color}')

    c_1 = int(lamp1.color[0] * D_r[smnode_id] * gain1)
    c_2 = int(lamp1.color[1] * D_g[smnode_id] * gain1)
    c_3 = int(lamp1.color[2] * D_b[smnode_id] * gain1)

    # c_1 = int(lamp1.color[0] * D_r[smnode_id])
    # c_2 = int(lamp1.color[1] * D_g[smnode_id])
    # c_3 = int(lamp1.color[2] * D_b[smnode_id])
    
    # motor message is list w/ seven items: unk, unk, unk, unk, r, g, b)
    # mot = [0,0,255, 255, abs(63-f), f, abs(191-f)//2] # esc, servopos, light
    # mot = [0,0,255, 255, int(f), 0, 0] # esc, servopos, light
    mot = [0,0,255, 255, c_1, c_2, c_3] # esc, servopos, light
    # print(f'    sm sending motors {mot}')
    # send motor message
    cord.set_raw_data_send(smnode_id, mot)
    # read sensor message
    x = cord.get_raw_data_recv(smnode_id, 11)
    # print(f'    sm reply {x}')
    # brightness sensors are 5 and 6
    # print(f'    sm receive sensors brightness {x[5]} {x[6]}')
    # sleep(0.01) # todo replace by framesync
    
    # # inner / outer loop OK
    # if loopcnt % 1000 == 0:
    #     if random.uniform(0, 1) > 0.8:
    #         lamp1.color = get_random_color()
    #         print(f'    new color = {lamp1.color}')

def smloop_event_handler(cord_close):
    # graphics update
    running = True
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # stopping motor cord
                running = cord_close()

        # loop timer
        pygame.time.wait(looprate_default_ms)

    except (KeyboardInterrupt, SystemExit):
        # stopping motor cord
        running = cord_close()
    return running
        
def smloop_example_node_io(smnode_id, loopcnt, cord, **kwargs):
    i = loopcnt
    
    f = sawtooth(i)

    mot = [0,0,0,0,f,f,f] # esc, servopos, light
    print(f"smloop example_node_io mot {mot}")
    # for b in range(cord.number_of_motors):
    cord.set_raw_data_send(smnode_id, mot)

    sen = cord.get_raw_data_recv(smnode_id, 11)
    print(f"smloop example_node_io sen {sen}")

def smloop_counter(smnode_id, loopcnt, cord, **kwargs):
    f = loopcnt % 255
            
    # motor message is list w/ seven items: unk, unk, unk, unk, r, g, b)
    mot = [0,0,255, 255, abs(63-f), f, abs(191-f)//2] # esc, servopos, light
    # mot = [0,0,255, 255, int(f), 0, 0] # esc, servopos, light
    print(f'smloop counter mot {mot}')
    # send motor message
    cord.set_raw_data_send(smnode_id, mot)
    # read sensor message
    sen = cord.get_raw_data_recv(smnode_id, 11)
    print(f'smloop counter sen {sen}')
            
    # brightness sensors are 5 and 6
    # print(f'    sm receive sensors brightness {x[5]} {x[6]}')
    # sleep(0.01) # todo replace by framesync
    
def main_smloop_shell(args, win, smloop_cb):
    """main example_node_io
    """
    if args.driver == 'libsensorimotor':
        from driver_libsensorimotor import cord_init, cord_close
    elif args.driver == 'osc':
        from driver_osc import cord_init, cord_close
    elif args.driver == 'dummy':
        from driver_dummy import cord_init, cord_close
        
    cord = cord_init()
    
    cord_close_cord = partial(cord_close, cord)

    # HACK
    if args.mode == "lischt":
        smloop_kwargs = smloop_lischt_init(cord)
    else:
        smloop_kwargs = {}

    smloop_kwargs['clock_freq'] = args.clock_freq

    # enter main loop: lombi sensorimotor loop
    loopcnt = 0
    running = True
    while running and cord.running():

        # for each smnode on the cord / bus
        # better: for smnode_id in range(cord.active_node_ids):
        for smnode_id in range(cord.number_of_motors):
            # smloop_example_node_io(smnode_id, loopcnt, cord)
            smloop_cb(smnode_id, loopcnt, cord, **smloop_kwargs)

        running = smloop_event_handler(cord_close_cord)
        loopcnt +=1

    # quit event and teardown pygame
    pygame.quit()

# main dummy
def main(args): pass

# ...
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="", dest="mode")

    subparser_example_node_io = subparsers.add_parser("example_node_io", help="example_node_io help")
    subparser_example_node_io.add_argument(
        '-c', '--clock-freq', type=float, default=0.10,
        help='Internal clock frequency [0.10Hz]')

    subparser_counter = subparsers.add_parser("counter", help="counter help")

    subparser_lischt = subparsers.add_parser("lischt", help="lischt help")
    subparser_lischt.add_argument(
        '-c', '--clock-freq', type=float, default=0.10,
        help='Internal clock frequency [0.10Hz]')

    parser.add_argument(
        '-d', '--driver', default="libsensorimotor",
        help='Which driver to use for talking to the hex [libsensorimotor] or osc')
    
    args = parser.parse_args()

    win = pygame.display.set_mode((wScreen, hScreen))
    # win = None

    if args.mode == 'lischt':
        smloop_callback = smloop_lischt
    elif args.mode == 'example_node_io':
        smloop_callback = smloop_example_node_io
    elif args.mode == 'counter':
        smloop_callback = smloop_counter
    else:
        main(args, win)
        
    main_smloop_shell(args, win, smloop_callback)
