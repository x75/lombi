"""oscsrv

Oswald's OSC server design pattern. Simple liblo based OSC server with
send/recv capability and custom callbacks registered from the calling
context.
"""
import re, threading, time
import liblo

class OSCsrv(object):
    def __init__(self, port=1234, queue=None):
        # thread init
        super(OSCsrv, self).__init__()
        # threading.Thread.__init__(self)
        
        self.server = None
        self.port = port
        self.queue = queue
        # self.name = 'OSCsrv'
        
        self.name = str(self.__class__).split(".")[-1].replace("'>", "")
        # signal.signal(signal.SIGINT, self.shutdown_handler)

        # rospy.init_node(self.name, anonymous=True)
        
        # self.isrunning = True
        # self.cnt_main = 0
        # self.loop_time = 0.1
        
        try:
            self.server = liblo.Server(self.port)
            print(f'oscsrv.OSCsrv server started on port {self.port}')
            self.isrunning = True
        except liblo.ServerError as err:
            print(err)
            self.isrunning = False
            # sys.exit()
            
        # register method taking an int and a float
        # self.server.add_method("/mfcc", 'i' + 'f' * 38, self.cb_mfcc)
        # self.server.add_method("/mfcc", 'i' + 'f' * 1024, self.cb_mfcc)
        # self.cb_mfcc_stats = {
        #     'cnt': 0,
        #     'seq': 0,
        #     'last': time.time(),
        #     'freq': 0.,
        #     'period_mu': 1000.,
        #     'period_var': 0.,
        # }
        # self.server.add_method("/beat", 'f' * 3, self.cb_beat)

        self.st = threading.Thread( target = self.run )
        self.st.start()
        
    def add_method(self, path, types, callback):
        callback_name = 'cb_{0}'.format(re.sub('/', '_', path))
        print('oscsrv.add_method for {0}'.format(callback_name))
        setattr(self, callback_name, callback)
        self.server.add_method(path, types, getattr(self, callback_name))

    # def cb_mfcc(self, path, args):
    #     # i, f = args
    #     # print("received message '%s' with arguments '%d' and '%f'" % (path, i, f))
    #     now = time.time()
    #     self.cb_mfcc_stats['cnt'] += 1
    #     seq_error = args[0] - self.cb_mfcc_stats['seq']
    #     if seq_error > 1:
    #         print(f'    seq_error = {seq_error}')
    #     self.cb_mfcc_stats['seq'] = args[0]
    #     now_period = now - self.cb_mfcc_stats['last']
    #     # print(f'now_period = {now_period}')
    #     self.cb_mfcc_stats['last'] = now
    #     self.cb_mfcc_stats['period_mu'] = 0.9 * self.cb_mfcc_stats['period_mu'] + 0.1 * now_period
    #     self.cb_mfcc_stats['freq'] = 1.0/self.cb_mfcc_stats['period_mu']
    #     now_error = abs(self.cb_mfcc_stats['period_mu'] - now_period)
    #     self.cb_mfcc_stats['period_var'] = 0.9 * self.cb_mfcc_stats['period_var'] + 0.1 * now_error
    #     # print('cb_mfcc_stats', self.cb_mfcc_stats)
    #     self.queue.put(args)
    #     # print('received args {0}'.format(args))

    # def cb_beat(self, path, args):
    #     print('got args = {0}'.format(args))
    #     self.queue.put(args)

    def run(self):
        print('oscsrv.OSCsrv run starting')
        # loop and dispatch messages every 100ms
        while self.isrunning:
            self.server.recv(100)
        print('oscsrv.OSCsrv run terminating')
