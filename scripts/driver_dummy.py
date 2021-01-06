"""Dummy driver libsensorimotor
"""

# import libsensorimotor for talking to the smnodes
# from util import SensorimotorDummy

import time

DEBUG=True

class SensorimotorDummy(object):
    def __init__(self, number_of_motors, verbose=DEBUG, update_rate_Hz=100):
        self.number_of_motors=number_of_motors
        self.verbose=DEBUG
        self.update_rate_Hz=update_rate_Hz
        self.running_flag = False

    def start(self):
        self.running_flag = True
        print(f'    start, running {self.running_flag}')

    def ping(self):
        print(f'    ping')
        return self.number_of_motors
        
    def running(self):
        return self.running_flag

    def apply_impulse(self, b):
        print(f'    apply_impulse {b}')

    def set_raw_data_send(self, ids_smnode, mot):
        print(f'    set_raw_data_send {ids_smnode} {mot}')

    def get_raw_data_recv(self, rxid, rxlen):
        print(f'    get_raw_data_recv {rxid} {rxlen}')
        return [rxid for _ in range(rxlen)]
        
    def stop(self):
        self.running_flag = False
        print(f'    stop, running {self.running_flag}')

def cord_init():
    # create sensorimotor communication bus
    cord = SensorimotorDummy(
        number_of_motors=6,   # how many motors
        verbose=False,        # print debug info
        update_rate_Hz = 100) # low-level update frequency

    try:
        # checking for motors
        N = cord.ping()
        print(f"drv_libsm cord_init found {N} sensorimotors.")
        time.sleep(0.25)

        # starting motorcord
        cord.start()
        i = 0
    except Exception as e:
        # Script crashed?
        print(f"drv_libsm cord_init Exception thrown, stopping cord. {e}")
        cord.stop()
        raise
    return cord

def cord_close(cord):
    print(f"drv_libsm cord_close, stopping motors")
    cord.stop()
    return False
