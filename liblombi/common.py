import time, math, random

looprate_default = 1/25.

TWOPI = 2*math.pi

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

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

