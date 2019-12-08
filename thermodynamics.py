# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 11:45:14 2018

@author: Alexx
"""

import numpy as np
import scipy as sp
from CoolProp.CoolProp import PropsSI as ps
import inputfile as vs


#Ideal Gas Constant

def Rgas():
    rval=0
    for key in vs.sw:
        rval+=vs.sw[key]/ps('molarmass','P',200,'T',200,key)
    R=8.344598*rval
    return R

#Specific thermal enthalpy

def hgas(T,P):
    hval=0
    for key in vs.sw:
        hval+=vs.sw[key]*ps('H','P',P,'T',T,key)
    return hval

#Specific heats ratio

def kgas(T,P):
    cpval=0
    cvval=0
    for key in vs.sw:
        cpval+=vs.sw[key]*ps('C','P',P,'T',T,key)
        cvval+=vs.sw[key]*ps('CVMASS','P',P,'T',T,key)
    kappa=cpval/cvval
    return kappa