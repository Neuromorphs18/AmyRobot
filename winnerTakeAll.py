import nengo
import numpy as np
import nengo_spa




# ----------------------------------------------------------------
model = nengo.Network()
with model:
    

    emotional_states = 4 # happy, distressed, sad, calm
 
    
    # ---------------------- NUCLEI ---------------------------------------
    central = nengo.Ensemble(n_neurons=128,dimensions=emotional_states) # a sparse representation of the input

   # central = nengo_spa.networks.selection.WTA(n_neurons=100, n_ensembles=emotional_states,
    #                                           threshold=0.3, 
    #                                           function=lambda x: 1 if x>0 else 0)
  
    
    # ---------------------- NODES ---------------------------------------------    
    
    #
    stim = nengo.Node(None, size_in=emotional_states)
    

    # ------------------ CONNECTIONS --------------------------------------- 
        
    # input stim to lateral
    nengo.Connection(stim,central)
    