"""osc2sensorimotor

bridge between OSC and libsensorimotor
"""
from __future__ import print_function
from time import sleep
from functools import partial

import sys, time, queue, pickle, argparse
import threading

import liblo
from src.sensorimotor import Sensorimotor
from driver_dummy import SensorimotorDummy
from oscsrv import OSCsrv

DEBUG = False

conflib = {
    'monkeydrummer': {
        'port': 1234,
        'number_of_motors': 3,
        'voltage_limits': [0.8] * 3,
        'update_rate_Hz': 100,
        'name': 'monkeydrummer',
        'smnode_ids': [0, 1, 2, 3, 4, 5],
        'dummy': False,
    },
    'hexagon': {
        'port': 1236,
        'number_of_motors': 6,
        'voltage_limits': [0.8] * 6,
        'update_rate_Hz': 100,
        'name': 'hexagon',
        'smnode_ids': [0, 1, 2, 3, 4, 5],
        'dummy': False,
    }
}

def loopfunc_monkeydrummer(qud, cord):
    b = qud
    print('beat b = {0}'.format(b))
    cord.apply_impulse(b)

def loopfunc_hexagon(qud, cord):
    # b = qud
    # print('loopfunc_hexagon qud = {0}'.format(qud))

    # # single vector for all smnodes
    # for b in range(cord.number_of_motors):
    #     led = int(qud[b])
    #     mot = [0,0,] # esc, servopos, light (id-high, id-low, r, g, b)
    #     cord.set_raw_data_send(b, mot)

    id_smnode = qud[0]
    # if id_smnode > 1: return
    id_high = 0
    id_low = 0
    rgb = qud[1:]
    mot = [0, 0, id_high, id_low] + list(rgb)
    # mot = [0, 0, id_high, id_low, 255, 255, 255]
    # print('loopfunc_hexagon send to smnode = {0}, mot = {1}'.format(id_smnode, mot))
    ids_smnode = [0, 1, 2, 3, 4, 5]
    cord.set_raw_data_send(ids_smnode[id_smnode], mot)
    # cord.apply_impulse(b)

def cb_hexagon_motors(qu, path, args, types, target, unk):
    # def cb_hexagon_motors(*args, **kwargs):
    # i, f = args
    # print('args = {0}, kwargs = {1}'.format(args, kwargs))
    # print('qu = {0}'.format(qu))
    # print("cb_hexagon_motors message {0} with arguments {1}".format(path, args))
    qu.put((path, args))
    # print('received args {0}'.format(args))
    
def main(args):
    conf = conflib[args.conf]
    args_main = argparse.Namespace()
    for conf_key in conf: # ['number_of_motors', 'update_rate_Hz', 'smnode_ids']:
        # update from command line
        if hasattr(args, conf_key) and getattr(args, conf_key) is not None:
            setattr(args_main, conf_key, getattr(args, conf_key))
        else:
            setattr(args_main, conf_key, conf[conf_key])

    # convenience
    args_main.update_period_s = 1./args_main.update_rate_Hz
    
    # create queue
    qu = queue.Queue(maxsize=10)

    # def cb_hexagon_motors(path, args, types, target, unk):
    #     # def cb_hexagon_motors(*args, **kwargs):
    #     # i, f = args
    #     # print('args = {0}, kwargs = {1}'.format(args, kwargs))
    #     # print('qu = {0}'.format(qu))
    #     print("cb_hexagon_motors message {0} with arguments {1}".format(path, args))
    #     qu.put((path, args))
    #     # print('received args {0}'.format(args))

    osc_address_motors = f"/{args_main.name}_motors"
    osc_address_sensors = f"/{args_main.name}_sensors"
    
    # create server, listening on port 1234
    oscsrv = OSCsrv(port=args_main.port, queue=qu)
    oscsrv.add_method(
        path=osc_address_motors,
        # types='f'*number_of_motors,
        types='iiii',
        # use a partial here to bind the qu argument
        callback=partial(cb_hexagon_motors, qu)
        # callback=cb_hexagon_motors,
    )

    # # fix pd
    # target = liblo.Address(1337)
    # liblo.send(target, "/reconnect", 'bang')
    osc_target_hub = liblo.Address(1237)
    osc_target_trigrid = liblo.Address('localhost', 1235, liblo.UDP)
    
    # init motors
    if not args_main.dummy:
        cord = Sensorimotor(
            number_of_motors=args_main.number_of_motors,
            verbose=DEBUG,
            update_rate_Hz=args_main.update_rate_Hz)
    else:
        cord = SensorimotorDummy(
            number_of_motors=args_main.number_of_motors,
            verbose=DEBUG,
            update_rate_Hz=args_main.update_rate_Hz
        )

    try:
        # checking for motors
        N = cord.ping()
        print("osc2sensorimotor.main found {0} sensorimotors".format(N))
        sleep(0.2)

        # # TODO: set this according to your supply voltage and desired max. motor speed
        # cord.set_voltage_limit([0.8, 0.8, 0.8])

        # starting motorcord
        cord.start()

        # beat = tst0
    except (Exception):
        print('osc2sensorimotor.main failed to start motors')
        pass
        

    # start loop
    beats = [[0.6, 0.0, 0.0], [0.0, 0.6, 0.0], [0.0, 0.0, 0.6]]
    cnt = 0
    try:
        while True:
            # print('main loop cnt = {0}'.format(cnt))
            qud = None
            while qu.qsize() > 0:
                qud = qu.get()
                # qud[0] = 0
                # print('qu {0}'.format(qud))
                # QUD[0,:] = np.array(qud)
                # QUD = np.roll(QUD, shift=1, axis=0)

                # print('qud = {0}'.format(qud))
                
                # USER CODE HERE BEGIN
                # motors.apply_impulse(b[0])
                # b = beats[cnt%3]
                if qud is not None:
                    loopfunc_hexagon(qud[1], cord)
            # time.sleep(1e-3)
                
            cnt += 1
            # print('cnt={0}'.format(cnt))
            
            if cnt % 1000 == 0:
                # gng.stop_training()
                
                # f = open('gng.bin', 'wb')
                # pickle.dump(gng, f)
                # f.close()
                print('cnt = {0}'.format(cnt))
                # pass

            for i in args_main.smnode_ids:
                x = cord.get_raw_data_recv(i, 11)
                if i == 1:
                    print(i, x)
                # print(x[5], x[6])
                l_ = [i] + x
                oscsrv.server.send(
                    osc_target_trigrid,
                    osc_address_sensors,
                    *l_
                )
            time.sleep(args_main.update_period_s)
            
    except (KeyboardInterrupt, SystemExit):
        print("key fin")
        oscsrv.isrunning = False
        # stopping motor cord
        print("\rAborted, stopping motors")
        cord.stop()
        # plt.ioff()
        # gng.stop_training()
        
    except:
        # Script crashed?
        print("\rException thrown, stopping cord.")
        cord.stop()
        raise

    print("____\nDONE.")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', type=str, help="Configuration name [hexagon]", default="hexagon")
    parser.add_argument('-d', '--dummy', action="store_true", default="False", help="Run in dummy mode and just print the OSC messages received [False]")
    parser.add_argument('-p', '--port', type=int, help="OSC server port [1234]", default=None)
    
    args = parser.parse_args()
    
    main(args)
