import nengo
import numpy as np
import nengo_loihi
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

    def redis_lateral_in(t):
        global r
        lateral_in = float(r.get('lateral_in'))
        return lateral_in
    RedisIn = nengo.Node(redis_lateral_in,size_out=1)

    def redis_lateral_2_central(t,x):
        global r
        r.set('lateral_2_central_0', x[0])
        r.set('lateral_2_central_1', x[1])
        r.set('lateral_2_central_2', x[2])
        return x
    def redis_lateral_2_basal(t,x):
        global r
        r.set('lateral_2_basal_0', x[0])
        r.set('lateral_2_basal_1', x[1])
        return x
    RedisOut_2_central = nengo.Node(redis_lateral_2_central, size_in=3)
    RedisOut_2_basal = nengo.Node(redis_lateral_2_basal, size_in=2)

    lateral = nengo.Ensemble(n_neurons=100, dimensions=1) # a sparse representation of the input

    input_data = [[-1],[1],[0.2],[-0.2],[0]]
    output_data = [[1,1],[-1,1],[0.5, -0.5],[0.5, -0.5],[0,0]]
    per_input = 1

    # TODO:figure this whole thing out
    def fast_reaction(x):
        joy = x
        happy = 0
        distressed = 0
        calm = 0

        if joy > 0.7:
            happy = 1
        elif joy < -0.7:
            distressed = 1
        else:
            calm = 0.2

        return happy, distressed, calm

    nengo.Connection(RedisIn, lateral)
    nengo.Connection(lateral, RedisOut_2_basal, eval_points=input_data, function=output_data,
                     scale_eval_points=False, transform=per_input)
    nengo.Connection(lateral, RedisOut_2_central, function=fast_reaction)

    # save out lateral
    fp_lateral = FileSpikeProbe('lateral_spike_data', size_in=lateral.n_neurons)
    nengo.Connection(lateral.neurons, fp_lateral, synapse=None)
    
    fpv_lateral  = FileValueProbe('lateral_value', size_in=lateral.dimensions)
    nengo.Connection(lateral, fpv_lateral, synapse=0.1)
