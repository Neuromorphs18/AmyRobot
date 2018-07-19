import nengo
import numpy as np


good = [0,1,3,10,14]
N = len(good)

n_neurons = 256
import nengo_brainstorm

model = nengo.Network()
nengo_brainstorm.add_params(model)

def sine_wave(t, offset):
    return np.sin(t*np.pi*2+offset)
    

with model:
    stim = nengo.Node(lambda t: [sine_wave(t, offset=off) for off in np.linspace(0, 2*np.pi, N+1)[:N]])
    p_ideal = nengo.Probe(stim)
    
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
        nengo.Connection(stim[i], c)
        nengo.Connection(c, ensembles[good[i]])
        
    output_a = nengo.Node(lambda t, x: x, size_in=N)
    p_a = nengo.Probe(output_a)
    for i in range(N):
        c = nengo.Node(lambda t,x: x, size_in=1, label='c%d'%i)
        nengo.Connection(ensembles[good[i]], c, function=relu)
        nengo.Connection(c, output_a[i])
        
    for i in range(N):
        for j in range(N):
            if i!=j:
                nengo.Connection(ensembles[good[i]], ensembles[good[j]], function=neg_relu)
        
    '''
    b = nengo.networks.EnsembleArray(n_ensembles=N,
                                     n_neurons=n_neurons,
                                     intercepts=nengo.dists.Uniform(0,1),
                                     encoders=nengo.dists.Choice([[1]]),
                                     )
    for i in range(N):
        nengo.Connection(a.ea_ensembles[i], b.ea_ensembles[i])
    #nengo.Connection(a.output, b.input)
            
    output_b = nengo.Node(lambda t, x: x, size_in=N)
    for i in range(N):
        c = nengo.Node(lambda t,x: x, size_in=1, label='c%d'%i)
        nengo.Connection(b.ea_ensembles[i], c)
        nengo.Connection(c, output_b[i])
       ''' 
