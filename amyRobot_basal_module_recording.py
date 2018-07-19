import nengo
import numpy as np
import nengo_spinnaker
import redis

r = redis.StrictRedis(host = '10.0.0.3',password='neuromorph')

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
