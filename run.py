from algo import SigComplex
from dataset import load_MultiTS
import json

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

# initiate an instance of SigComplex
com = SigComplex(MultiTS, win = params["win"], alpha_1d = params["alpha_1d"], alpha_2d = params["alpha_2d"])

# create simplicial complex along T
com.complex_along_T()

# proportion of order violatio
com.order_violation([0])
# for fMRI case: com.complexT[0].numberOfSimplicesOfOrder()
# no 2-simplex are created


# visualize complex
com.layout([0])






