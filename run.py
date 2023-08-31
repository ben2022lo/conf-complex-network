from algo import SigComplex
from dataset import load_MultiTS
import json
import matplotlib.pyplot as plt

# parse configs
with open('configs.json', 'r') as f:
    configs=f.read()
params = json.loads(configs)

# load data
if params["dataset"] == "finance":
    MultiTS = load_MultiTS(params["dataset"])
elif params["dataset"] == "fMRI":
    # only one individu is considered for now
    MultiTS = load_MultiTS(params["dataset"])[0]  
elif params["dataset"] == "SOS":
    MultiTS = load_MultiTS(params["dataset"])
    
    
# initiate an instance of SigComplex
com = SigComplex(MultiTS, win = params["win"], alpha_1d = params["alpha_1d"], alpha_2d = params["alpha_2d"])

a = 0; b = 20 
# create simplicial complex along T
com.complex_along_T(a,b)

# proportion of order violation
com.order_violation(list(range(b)))
# hyper coherence
com.hyper_coherenceT[a:b]

# life duration distribution of 2-simplex
plt.hist(com.life_duration.values())
com.life_duration.keys()
len(com.life_duration.values())
for i in range(a,b):
    print(len(com.complexT[i].simplicesOfOrder(2)))

# visualization

import numpy as np
from simplicial import*
from simplicial import drawing

class New_Embedding(Embedding):
    '''
    Override the method computePositionOf(self, s: Simplex) for positioning 0-simplex
    '''
    def computePositionOf(self, s: Simplex):
        x = np.pi/6      
        k = int(s)
        pos = [np.cos(k*x),np.sin(k*x)]        
        return pos
for cs in com.complexT[a:b]:
    em = New_Embedding(cs, dim=2)
    drawing.draw_complex(cs, em, ax=None, color=None, color_simplex=None, node_size=0.05)
    plt.show()


