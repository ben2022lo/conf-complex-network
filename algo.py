import numpy as np
import signatory
import torch
from itertools import combinations
from sklearn.linear_model import Lasso
from simplicial import*


class SigComplex:
    def __init__(self, MultiTS, win, alpha_1d = 1000, alpha_2d = 1000):
        self.MultiTS = MultiTS 
        self.win = win
        self.T = MultiTS.shape[-2]
        self.D = MultiTS.shape[-1]
        self.alpha_1d = alpha_1d
        self.alpha_2d = alpha_2d
        self.complexT = [None] * MultiTS.shape[-2] # list to stock simplicial complex 
        self.hyper_coherenceT = [None] * MultiTS.shape[-2] # list to stock hyper coherence
        self.life_duration = {}
        
    def leadlag(self, X):
        '''
        lead-lag transformation of one dimensional TS [T,1] -> [2T-1, 2] 

        Parameters
        ----------
        X : tensor
            Time serie tensor of size [1,T,1]

        Returns
        -------
        TS_ll : tensor
            Time serie tensor of size [1,2T-1,2]

        '''
        TS_ll = []
        tuple_list = [(index, value) for index, value in enumerate(X.flatten().tolist())]

        for j in range(2*(len(tuple_list))-1):
            i1=j//2
            i2=j//2
            if j%2!=0:
                i1+=1
            TS_ll.append((tuple_list[i1][1], tuple_list[i2][1]))
        TS_ll = torch.tensor(TS_ll).view(1,59,2)
        return TS_ll

    def simplex_1d(self,t):     
        '''
        Compute augmented signatures of TS and perform lasso regression to create a adjacent matrix

        Parameters
        ----------
        t : int

        Returns
        -------
        adj_mat_1d : numpy.array
            adjacent matrix

        '''
        k = int(1)
        depth = 2
        k_uplets = list(combinations(np.arange(self.D),k))
        adj_mat_1d = np.zeros([len(k_uplets),len(k_uplets)])
        
        # compute (augmented) signature features for all k-uplets
        df_sig = np.zeros([(k+1)**depth+(k+1),len(k_uplets)]) 
        for i in range(len(k_uplets)):
            TS_group = torch.cat( 
                                (self.MultiTS[:,t:t+self.win,(i,)],torch.tensor(np.arange(t,t+self.win).reshape(1,self.win,1))) , 
                                 dim=2)
            df_sig[:,i] = signatory.signature(TS_group,depth=depth)
        # for each k-uplet, select his neighbors by lasso 
        for i in range(len(k_uplets)): 
            clf = Lasso(alpha=self.alpha_1d) # choice of alpha depends of dataset, but generaly large for our configuration
            # get k-uplets which have distinct elements from the elements of target k-uplet
            indices = np.array([j for j, tup in enumerate(k_uplets) 
                                if tup[0] != k_uplets[i] ])                 
            # regression by lasso
            clf.fit(df_sig[:,indices],df_sig[:,i])
            # only regresion with R2 > 0.67 are kept
            w = clf.score(df_sig[:,indices],df_sig[:,i])
            print(w)
            if w > 0.67 :
                adj_mat_1d[indices[np.nonzero(clf.coef_)], i] = clf.coef_[clf.coef_ != 0]
        return adj_mat_1d
    
    def simplex_2d(self,t):
        '''
        Lasso regressions are applied between signatures (depth 2) of couples of TS (predictors) and lead-lag transformation of one TS (target)

        Parameters
        ----------
        t : t

        Returns
        -------
        adj_mat_2d : numpy.array
            adjacent matrix
        k_uplets : list
            all possible combinations of couples
        '''
        k = int(2)
        depth = 2
        k_uplets = list(combinations(np.arange(self.D),k))
        adj_mat_2d = np.zeros([self.D,len(k_uplets)])

        # compute signature features for all k-uplets
        df_sig_predictors = np.zeros([k**depth + k,len(k_uplets)]) 
        for i in range(len(k_uplets)):
            df_sig_predictors[:,i] = signatory.signature(self.MultiTS[:,t:t+self.win,k_uplets[i]], depth=depth)
        
        # compute signature features of lead-lag transformation of target
        df_sig_target = np.zeros([k**depth + k,self.D])
        for d in range(self.D):
            TS_ll = self.leadlag(self.MultiTS[:,t:t+self.win,(d,)])
            df_sig_target[:,d] = signatory.signature(TS_ll, depth = depth)
        
        # for each node, select his edge neighbors by lasso 
        for i in range(self.D): 
            clf = Lasso(alpha=self.alpha_2d) # choice of alpha depends of dataset, but generaly large for our configuration
            # get k-uplets which have distinct elements from the elements of target k-uplet
            indices = np.array([j for j, tup in enumerate(k_uplets) if tup[0] != i and tup[1] != i ])                 
            # regression by lasso
            clf.fit(df_sig_predictors[:,indices],df_sig_target[:,i])
            # only regresion with R2 > 0.67 are kept
            w = clf.score(df_sig_predictors[:,indices],df_sig_target[:,i])
            print(w)
            if w > 0.67 :
                    adj_mat_2d[i, indices[np.nonzero(clf.coef_)]] = clf.coef_[clf.coef_ != 0]
        return adj_mat_2d, k_uplets
        
    def complex_creation(self,t):
        '''
        Core method to creat complex, the simplices are added by order (0 -> 1 ->2)
        The simplices are defined by the prediction capability of their signatures feartures 
        2-simplex that violate order rules are kept by adding low-order simplices to the complex
        Parameters
        ----------
        t : int
        
        Returns
        -------
        c : SimplicialComplex

        '''
        # initialize complex
        c = SimplicialComplex()
        # add 0-simplex
        for d in range(self.D):
            _ = c.addSimplex(id = str(d))
        # adjance matrix between 0-simplices
        adj_mat_1d = self.simplex_1d(t)
        # Add 1-simplex with weight
        for i in range(adj_mat_1d.shape[0]):
            for j in range(i + 1, adj_mat_1d.shape[1]):  # Only add edges once (above the main diagonal)
                if adj_mat_1d[i,j] != 0 or adj_mat_1d[j,i] != 0:
                    # when two 0-simplices are predictor of each other, the weight become the sum of their coefficients
                    _ = c.addSimplex(fs = [str(i),str(j)], 
                                 id=str(i) + '-' + str(j), 
                                 attr=dict(weight=adj_mat_1d[i,j]+adj_mat_1d[j,i]))
                    print("add ",str(i) + '-' + str(j))
        print("Epoch : ",t," 1-simplex")
        # adjance matrix between 0-simplice and 1-simplices
        adj_mat_2d, k_uplets = self.simplex_2d(t)
        # Add 2-simplex with weight
        count_without = 0 # hyper coherence : 2-simplex without 3 1-simplices
        count_with = 0 # hyper coherence : 2-simplex with 3 1-simplices
        for i in range(adj_mat_2d.shape[0]):
            for j in range(adj_mat_2d.shape[1]):
                if adj_mat_2d[i,j] != 0:
                    try:
                        name = [i,k_uplets[j][0],k_uplets[j][1]]
                        name.sort()
                        id1 =  str(name[0]) + '-' + str(name[1]) + '-' + str(name[2]) 
                        _, completed = c.addSimplexWithBasis(bs = [str(i),str(k_uplets[j][0]),str(k_uplets[j][1])], 
                                     id = id1,
                                     attr=dict(weight= adj_mat_2d[i,j]))                    
                        self.life_duration[id1] = self.life_duration[id1] + 1 if id1 in self.life_duration else 1
                        print('add ', id1)
                        if completed:
                            count_without += 1
                            
                        else :
                            count_with += 1                           
                    # when same basis (0-simlex) are found, all coeffients are added to the weight
                    except:
                        simplex_id = c.simplexWithBasis(bs=[str(i),str(k_uplets[j][0]),str(k_uplets[j][1])])
                        c[simplex_id]["weight"] = c[simplex_id]["weight"] + adj_mat_2d[i,j]                 
                    
        print("Epoch : ",t," 2d-simplex")
        hyper_coherence = count_without/count_with
        return c, hyper_coherence
    
    def complex_along_T(self,a,b):
        '''
        This method generate complex for a given period

        '''
        for t in range(a,b): 
            self.complexT[t], self.hyper_coherenceT[t] = self.complex_creation(t)
            
    
    def order_violation(self, list_t):
        '''
        This method study the coherence level of simplicial complex by looking at if 2-simplices
        found by lasso have already necessary lower order simplices 
        
        Parameters
        ----------
        list_t : list
            indices of complex to be considered.

        Returns
        -------
        prop_violations : list
            list of violations proportions : 
                number of 1-simplices added / total number of 1-simplices to create 2-simplices

        '''
        prop_violations = []
        for t in list_t:
            complex_t = self.complexT[t]
            count = 0
            for i in complex_t.simplices():
                if "d" in i:
                    count += 1
            prop_violations.append(count/(complex_t.numberOfSimplicesOfOrder()[2]*3))
        return prop_violations
    
    def layout(self, list_t):
        '''
        This method try to visualize complex, the Embedding class need to be overrided
        
        Parameters
        ----------
        list_t : list
            indices of complex to be considered..

        Returns
        -------
        None.

        '''
        for t in list_t:          
            em = Embedding(self.complexT[t], dim=2)
            drawing.draw_complex(self.complexT[t], em, ax=None, color=None, color_simplex=None, node_size=0.02)
