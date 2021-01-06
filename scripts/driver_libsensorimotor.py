import time
# import libsensorimotor for talking to the smnodes
from src.sensorimotor import Sensorimotor

def cord_init():
    # create sensorimotor communication bus
    cord = Sensorimotor(
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
