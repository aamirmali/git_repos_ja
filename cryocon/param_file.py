import numpy as np
import pickle

class Params:
    def __init__(self,sp_res,P,I,D,factor,num):
        self.sp_res=sp_res
        self.P=P
        self.I=I
        self.D=D
        self.factor=factor
        self.num=num


def write_params(filename, params):
    pickle.dump(params,open(filename,'wb'))

def get_params(filename):
    par=pickle.load(open(filename,'rb'))
    return par

