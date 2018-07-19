import nengo
import numpy as np
#import nengo_loihi
import redis

r = redis.StrictRedis(host = '10.0.0.3',password='neuromorph')

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

    def fast_reaction(x):
        joy = x
        happy = 0
        distressed = 0
        calm = 0

        if joy > 0.8:
            happy = 1
        elif joy < -0.8:
            distressed = 1
        else:
            calm = 0.2

        return happy, distressed, calm

    nengo.Connection(RedisIn, lateral)
    nengo.Connection(lateral, RedisOut_2_basal, eval_points=input_data, function=output_data,
                     scale_eval_points=False, transform=per_input)
    nengo.Connection(lateral, RedisOut_2_central, function=fast_reaction)
