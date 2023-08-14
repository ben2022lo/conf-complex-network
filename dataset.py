import pandas as pd
import torch
from scipy import io
from os import listdir
#import numpy as np

def load_MultiTS(dataset):
    if dataset == "finance":
        # load data
        df = pd.read_csv("All_data_MTS/Financial_data/NYSE_119stocks_2000Jan_2021June_withdates.csv")
        # preprocessing for signature computation
        array_data = df.iloc[:,1:].to_numpy()
        reshaped_array = array_data.reshape((1, *array_data.shape))
        MultiTS = torch.tensor(reshaped_array)
        return MultiTS
    
    if dataset == "fMRI":
        l_MultiTS = []
        for individu in listdir("All_data_MTS/HCP_data/HCP_TS"):
            dic = io.loadmat("All_data_MTS/HCP_data/HCP_TS/"+individu+"/rfMRI_REST1_LR/Schaefer100/TS_Schaefer100S_gsr_bp_z.mat")
            array_data = dic["TS"].T
            MultiTS = array_data.reshape((1, *array_data.shape))
            l_MultiTS.append(torch.tensor(MultiTS))
        return l_MultiTS
    # too many missing values
    #if dataset == "epidemie":
    #    disease_dic = {}
    #    for disease in listdir("All_data_MTS/Epidemic"):
    #        if "csv" in disease and "MEASLES" not in disease:
    #            name = disease[:disease.find('_')]
    #            disease_dic[name] = pd.read_csv("All_data_MTS/Epidemic/" + disease, skiprows=2)
    #    for name in disease_dic.keys():
    #        print("---------------------")
    #        print(name)
    #        print(disease_dic[name])
    #        disease_dic[name].replace('-', np.nan, inplace=True)
    #        print(disease_dic[name].isna().mean())
    
    raise ValueError("Unsupported dataset: " + dataset)
   



