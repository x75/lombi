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
import argparse, os, pprint, time, sys
# math / numerical imports
import math, random
# import numpy as np
from functools import partial

# TODO: make these imports optional
# import pygame game engine for (internal) simulation
import pygame

from liblombi.smloops import (
    # lischt
    smloop_lischt_init,
    smloop_lischt,
    # example_node_io
    smloop_example_node_io,
    smloop_example_node_io_outer,
    # counter
    smloop_counter,
    smloop_multicounter,
    TWOPI
)

#########################################################
# lombi configuration


# display configuration
wScreen = 900
hScreen = 800

# color defaults
lamp_col_default = (255,203,125)
lamp_col_excited = (203,255,255)

loopfreq_default = 25
looprate_default = 1/loopfreq_default
looprate_default_ms = int(looprate_default * 1000)

from liblombi.common import (
    is_raspberrypi,
    print_vec,
    sawtooth,
    get_random_color,
    clock,
    get_frequency_modulator,
    get_color_modulator
)

if is_raspberrypi():
    # import raspi hardware driver
    import RPi.GPIO as GPIO

############################################################
# sensorimotor loop shell
def smloop_event_handler(cord_close):
    """smloop_event_handler

    Event handling callback for smloop shell
    """
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
        
def main_smloop_shell(args, win, smloop_cb, smloop_cb_outer, smloop_init):
    """main_smloop_shell

    The main smloop shell
    """
    if args.driver == 'libsensorimotor':
        from driver_libsensorimotor import cord_init, cord_close
    elif args.driver == 'osc':
        from driver_osc import cord_init, cord_close
    elif args.driver == 'dummy':
        from driver_dummy import cord_init, cord_close
        
    cord = cord_init()
    
    cord_close_cord = partial(cord_close, cord)

    smloop_kwargs = {}
    if smloop_init is not None:
        smloop_kwargs.update(smloop_init(cord))

    # HACK
    for attr in ['clock_freq', 'verbose', 'gain']:
        if hasattr(args, attr):
            smloop_kwargs[attr] = getattr(args, attr)
    
    # enter main loop: lombi sensorimotor loop
    loopcnt = 0
    running = True
    while running and cord.running():

        if smloop_cb_outer is not None:
            smloop_cb_outer(None, loopcnt, cord, **smloop_kwargs)

        else:
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
def main(args, *stuff): pass

# ...
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="", dest="mode")

    subparser_example_node_io = subparsers.add_parser("example_node_io", help="example_node_io help")
    subparser_example_node_io.add_argument(
        '-c', '--clock-freq', type=float, default=0.10,
        help='Internal clock frequency [0.10Hz]')

    subparser_counter = subparsers.add_parser("counter", help="counter help")

    subparser_multicounter = subparsers.add_parser("multicounter", help="multicounter help")
    
    subparser_lischt = subparsers.add_parser("lischt", help="lischt help")
    subparser_lischt.add_argument(
        '-c', '--clock-freq', type=float, default=0.10,
        help='Internal clock frequency [0.10Hz]')

    parser.add_argument(
        '-d', '--driver', default="libsensorimotor",
        help='Which driver to use for talking to the hex [libsensorimotor] or osc')
    parser.add_argument(
        '-g', '--gain', default=1.0,
        help='Sum output gain [1.0] in 0 ... 1')
    parser.add_argument(
        '-v', '--verbose', default=False, action="store_true",
        help='Be verbose [False]')
    
    args = parser.parse_args()

    win = pygame.display.set_mode((wScreen, hScreen))
    # win = None

    smloop_init = None
    smloop_callback = None
    smloop_callback_outer = None
    if args.mode == 'lischt':
        smloop_init = smloop_lischt_init
        smloop_callback_outer = smloop_lischt
    elif args.mode == 'example_node_io':
        # smloop_callback = smloop_example_node_io
        smloop_callback_outer = smloop_example_node_io_outer
    elif args.mode == 'counter':
        smloop_callback = smloop_counter
    elif args.mode == 'multicounter':
        smloop_callback = smloop_multicounter
    else:
        main(args, win)
        sys.exit()
        
    main_smloop_shell(args, win, smloop_callback, smloop_callback_outer, smloop_init)
