from algo import SigComplex
from dataset import load_MultiTS
import json

# parse configs
with open('configs.json', 'r') as f:
    configs=f.read()
params = json.loads(configs)

# load data
MultiTS = load_MultiTS(params["dataset"])

# initiate an instance of SigComplex
com = SigComplex(MultiTS, win = params["win"], alpha_1d = params["alpha_1d"], alpha_2d = params["alpha_2d"])

# create simplicial complex along T
com.complex_along_T()

# proportion of order violatio
com.order_violation([0])

# visualize complex
com.layout([0])






