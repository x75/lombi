"""lombi.smloops

Sensorimotor loop definitions for lombi
"""
import random, math

from liblombi.common import (
    sawtooth, get_random_color, get_frequency_modulator,
    get_color_modulator, clock, TWOPI
)

looprate_default = 1/25.

############################################################
# smloop mode: lischt

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
    # lamp1 = kwargs['lamp1']

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

    # set lamp object brightness via its gain
    # lamp1.gain = D_r[0]
    # print(f'    D_r = {D_r}')
    gain1 = 0.5
    # for each smnode on the cord / bus
    for smnode_id in range(cord.number_of_motors):
        # color modulators
        D_phi_r, D_r = get_color_modulator(smnode_id, D_phi_r, D_r, looprate_default, T, T_r)
        D_phi_g, D_g = get_color_modulator(smnode_id, D_phi_g, D_g, looprate_default, T, T_g)
        D_phi_b, D_b = get_color_modulator(smnode_id, D_phi_b, D_b, looprate_default, T, T_b)
        
        # construct low-level motor message
        # f = int(D_r[smnode_id] * 255) # scale daylight value to 8 bit and make integer
        # f_ = D_r[smnode_id] # scale daylight value to 8 bit and make integer
        # print(f'    f = {f}, color = {lamp1_color}')

        c_1 = int(lamp1_color[0] * D_r[smnode_id] * gain1)
        c_2 = int(lamp1_color[1] * D_g[smnode_id] * gain1)
        c_3 = int(lamp1_color[2] * D_b[smnode_id] * gain1)

        # c_1 = int(lamp1_color[0] * D_r[smnode_id])
        # c_2 = int(lamp1_color[1] * D_g[smnode_id])
        # c_3 = int(lamp1_color[2] * D_b[smnode_id])

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
        
    # inner / outer loop OK
    if loopcnt % 1000 == 0:
        if random.uniform(0, 1) > 0.8:
            lamp1_color = get_random_color()
            kwargs['lamp1_color'] = lamp1_color
            print(f'    new color = {lamp1_color}')

############################################################
# smloop mode: example_node_io
def smloop_example_node_io(smnode_id, loopcnt, cord, **kwargs):
    i = loopcnt
    
    f = sawtooth(i)

    mot = [0,0,0,0,f,f,f] # esc, servopos, light
    print(f"smloop example_node_io mot {mot}")
    # for b in range(cord.number_of_motors):
    cord.set_raw_data_send(smnode_id, mot)

    sen = cord.get_raw_data_recv(smnode_id, 11)
    print(f"smloop example_node_io sen {sen}")

def smloop_example_node_io_outer(smnode_id, loopcnt, cord, **kwargs):
    # f = sawtooth(i)

    # mot = [0,0,0,0,f,f,f] # esc, servopos, light
    # print(f"smloop example_node_io_outer mot {mot}")
    for smnode_id in range(cord.number_of_motors):
        i = loopcnt
        b = smnode_id
        # original loop body from example_node_io.py
        f = sawtooth(b*85 + i)
        g = sawtooth(b*85 + i + 128)
        mot = [0,0,255,255,255-f,f,255-g] # esc, servopos, light
        cord.set_raw_data_send(b, mot)

        
    for smnode_id in range(cord.number_of_motors):
        sen = cord.get_raw_data_recv(smnode_id, 11)
        print(f"smloop example_node_io_outer sen {sen}")



############################################################
# smloop mode: counter
def smloop_counter(smnode_id, loopcnt, cord, **kwargs):
    f = int((math.sin(((loopcnt % 256)/128 - 1) * TWOPI * 0.1) + 1) * 127)
    # motor message is list w/ seven items: unk, unk, unk, unk, r, g, b)
    mot = [0,0,255, 255, abs(63-f), f, abs(191-f)//2] # esc, servopos, light
    # mot = [0,0,255, 255, int(f), 0, 0] # esc, servopos, light
    print(f'smloop counter mot {mot}')
    # send motor message
    cord.set_raw_data_send(smnode_id, mot)
    # read sensor message
    sen = cord.get_raw_data_recv(smnode_id, 11)
    # print(f'smloop counter sen {sen}')
            
    # brightness sensors are 5 and 6
    # print(f'    sm receive sensors brightness {x[5]} {x[6]}')
    # sleep(0.01) # todo replace by framesync
    
############################################################
# smloop mode: multicounter
def smloop_multicounter(smnode_id, loopcnt, cord, **kwargs):
    arg = loopcnt / 25
    r = int((math.sin(arg * TWOPI * 0.11) + 1) * 127)
    g = int((math.sin(arg * TWOPI * 0.12) + 1) * 127)
    b = int((math.sin(arg * TWOPI * 0.13) + 1) * 127)

    # create motor message
    mot = [0,0,255, 255, r, g, b] # esc, servopos, light
    # print(f'smloop multicounter mot {mot}')

    # send motor message
    cord.set_raw_data_send(smnode_id, mot)
    
    # read sensor message
    sen = cord.get_raw_data_recv(smnode_id, 11)
    # print(f'smloop counter sen {sen}')

