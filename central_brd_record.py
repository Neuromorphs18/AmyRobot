import nengo
import numpy as np
import nengo_brainstorm
import redis
import struct
import timeit

class FileSpikeProbe(nengo.Node):
    def __init__(self, filename, size_in, flush_every=1.0):
        self.filename = filename
        self.flush_every = flush_every
        self.last_flush = timeit.default_timer()
        self.f = open(filename, 'ab')
        super(FileSpikeProbe, self).__init__(self.update, size_in=size_in, size_out=0)
    def update(self, t, x):
        nengo_time = t
        clock_time = timeit.default_timer()
        indices = np.where(x!=0)[0]
        count = len(indices)
        msg = struct.pack('ffI'+'I'*count, nengo_time, clock_time, count, *indices)
        self.f.write(msg)
        if clock_time > self.last_flush + self.flush_every:
            self.f.flush()
            self.last_flush = clock_time
    def close(self):
        self.f.close()

class FileValueProbe(nengo.Node):
    def __init__(self, filename, size_in, flush_every=1.0):
        self.filename = filename
        self.flush_every = flush_every
        self.last_flush = timeit.default_timer()
        self.f = open(filename, 'ab')
        self.f.write(struct.pack('I', size_in))
        super(FileValueProbe, self).__init__(self.update, size_in=size_in, size_out=0)
    def update(self, t, x):
        nengo_time = t
        clock_time = timeit.default_timer()
        count = self.size_in
        msg = struct.pack('ff'+'f'*count, nengo_time, clock_time, *x)
        self.f.write(msg)
        if clock_time > self.last_flush + self.flush_every:
            self.f.flush()
            self.last_flush = clock_time
    def close(self):
        self.f.close()

r = redis.StrictRedis(host = '10.0.0.2',password='neuromorph')

good = [0,1,5]
N = len(good)
n_neurons = 256

model = nengo.Network()
nengo_brainstorm.add_params(model)
with model:
    def redis_WTA_in(t):
        global r
        WTA_in_0 = float(r.get('WTA_in_0'))
        WTA_in_1 = float(r.get('WTA_in_1'))
        WTA_in_2 = float(r.get('WTA_in_2'))
        return [WTA_in_0, WTA_in_1, WTA_in_2]
    RedisIn = nengo.Node(redis_WTA_in,size_out=3)
    
    def redis_WTA_out(t,x):
        global r
        r.set('WTA_out_0',x[0])
        r.set('WTA_out_1',x[1])
        r.set('WTA_out_2',x[2])
        return
    RedisOut = nengo.Node(redis_WTA_out,size_in=3)
    
    def relu(x):
        return max(x, 0)
    def neg_relu(x):
        return -max(x, 0)
    
    ensembles = []
    for i in range(16):
        ensembles.append(nengo.Ensemble(
                                     n_neurons=n_neurons,
                                     dimensions=1,
                                     intercepts=nengo.dists.Uniform(0,1),
                                     encoders=nengo.dists.Choice([[1]]),
                                     ))
    for i in range(N):
        c = nengo.Node(lambda t,x: x, size_in=1, label='c%d'%i)
        nengo.Connection(RedisIn[i], c)
        nengo.Connection(c, ensembles[good[i]])
        
    for i in range(N):
        c = nengo.Node(lambda t,x: x, size_in=1, label='c%d'%i)
        nengo.Connection(ensembles[good[i]], c, function=relu)
        nengo.Connection(c, RedisOut[i])
        
    for i in range(N):
        for j in range(N):
            if i!=j:
                nengo.Connection(ensembles[good[i]], ensembles[good[j]], function=neg_relu)

    # save out WTA0
    fp_wta0 = FileSpikeProbe('central_wta0_spike_data', size_in=ensembles[0].n_neurons)
    nengo.Connection(ensembles[0].neurons, fp_wta0, synapse=None)
    
    fpv_wta0  = FileValueProbe('central_wta0_value', size_in=ensembles[0].dimensions)
    nengo.Connection(ensembles[0], fpv_wta0, synapse=0.1)

    # save out WTA1
    fp_wta1 = FileSpikeProbe('central_wta1_spike_data', size_in=ensembles[1].n_neurons)
    nengo.Connection(ensembles[1].neurons, fp_wta1, synapse=None)
    
    fpv_wta1  = FileValueProbe('central_wta1_value', size_in=ensembles[1].dimensions)
    nengo.Connection(ensembles[1], fpv_wta1, synapse=0.1)

    # save out WTA2
    fp_wta2 = FileSpikeProbe('central_wta2_spike_data', size_in=ensembles[5].n_neurons)
    nengo.Connection(ensembles[5].neurons, fp_wta2, synapse=None)
    
    fpv_wta2 = FileValueProbe('central_wta2_value', size_in=ensembles[5].dimensions)
    nengo.Connection(ensembles[5], fpv_wta2, synapse=0.1)





                
                