import pandas as pd
import torch

def load_MultiTS(dataset):
    if dataset == "finance":
        # load data
        df = pd.read_csv("All_data_MTS/Financial_data/NYSE_119stocks_2000Jan_2021June_withdates.csv")
        # preprocessing for signature computation
        array_data = df.iloc[:,1:].to_numpy()
        reshaped_array = array_data.reshape((1, *array_data.shape))
        MultiTS = torch.tensor(reshaped_array)
    if dataset == "fMRI":
        pass
    if dataset == "epidemie":
        pass
    return MultiTS
