import nengo
import numpy as np
import nengo_spinnaker
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

model = nengo.Network()
with model:
    per_current_state = 1
    per_input = 2
    
    def redis_basal_in(t):
        global r
        basal_in_0 = float(r.get('basal_in_0'))
        basal_in_1 = float(r.get('basal_in_1'))
        return [basal_in_0, basal_in_1]
    RedisIn = nengo.Node(redis_basal_in,size_out=2)
    
    def redis_basal_out(t,x):
        global r
        r.set('basal_out_0',x[0])
        r.set('basal_out_1',x[1])
        r.set('basal_out_2',x[2])
        return
    RedisOut = nengo.Node(redis_basal_out, size_in=3)
    
    cortex = nengo.Ensemble(n_neurons=100, dimensions=2)
    basal = nengo.Ensemble(n_neurons=100, dimensions=2)
    
    emotion_matrix = np.array([
        [1, 1], # happy
        [-1, 1], # distressed
        [1, -1], # calm
        ])
        
    nengo.Connection(RedisIn, basal)
    nengo.Connection(basal, cortex)
    nengo.Connection(cortex, basal, transform=per_current_state)
    nengo.Connection(basal, RedisOut, transform=emotion_matrix)

    # save out data to files
    #fp_cortex = FileSpikeProbe('cortex_spike_data', size_in=cortex.n_neurons)
    #nengo.Connection(cortex.neurons, fp_cortex, synapse=None)
    
    fpv_cortex = FileValueProbe('cortex_value', size_in=cortex.dimensions)
    nengo.Connection(cortex, fpv_cortex, synapse=0.1)

    #fp_basal = FileSpikeProbe('basal_spike_data', size_in=basal.n_neurons)
    #nengo.Connection(basal.neurons, fp_basal, synapse=None)
    
    fpv_basal = FileValueProbe('basal_value', size_in=basal.dimensions)
    nengo.Connection(basal, fpv_basal, synapse=0.1)
