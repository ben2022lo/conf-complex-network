import numpy as np
import pandas as pd
import seaborn as sns
import signatory
import torch
from itertools import combinations
from sklearn.linear_model import Lasso

# load data
data = pd.read_csv("NYSE_119stocks_2000Jan_2021June_withdates.csv")

# preprocessing for signature computation
array_data = data.iloc[:,1:].to_numpy()
reshaped_array = array_data.reshape((1, *array_data.shape))
tensor = torch.tensor(reshaped_array)
T = tensor.shape[-2]
D = tensor.shape[-1]

# hyperparameters
k = int(2) # size of groups of TS
depth = k # depth of signature 
win = 30 # window size
alpha = 1200 # lasso regularization

# Generate all combinations of k-uplets
my_list = np.arange(D)
k_uplets = list(combinations(my_list, k))

# Initialize agency matrix of the graph (node being k-uplet) 
G = np.zeros([1, len(k_uplets),len(k_uplets)]) # change the constant by T-win

# find topological structure using lasso along t with signature features along t
for t in range(1): # change the constant by T-win
    # compute signature features for all k-uplets
    df_sig = np.zeros([k**depth + k,len(k_uplets)]) 
    for i in range(len(k_uplets)):
        df_sig[:,i] = signatory.signature(tensor[:,t:t+win,k_uplets[i]], depth=depth)
    # for each k-uplet, select his neighbors by lasso 
    for i in range(10): #len(k_uplets)
        clf = Lasso(alpha=alpha) # choice of alpha depends of dataset, but generaly large for our configuration
        # get k-uplets which have distinct elements from the elements of target k-uplet
        indices = np.array([j for j, tup in enumerate(k_uplets) 
                   if tup[0] != k_uplets[i][0] and tup[0] != k_uplets[i][1] and tup[1] != k_uplets[i][0] and tup[1] != k_uplets[i][1]])                 
        # regression by lasso
        clf.fit(df_sig[:,indices],df_sig[:,i])
        # only regresion with R2 > 0.67 are kept
        w = clf.score(df_sig[:,indices],df_sig[:,i])
        if w > 0.67 :
            G[t, indices[np.nonzero(clf.coef_)], i] = clf.coef_[clf.coef_ != 0]




