import nengo
import numpy as np
import nengo_brainstorm
import redis

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
                
                