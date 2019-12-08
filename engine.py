# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 11:46:39 2018

@author: Alexx
"""

import numpy as np
from CoolProp.CoolProp import PropsSI as ps
import matplotlib.pyplot as plt
import inputfile as vs
import thermodynamics as th

#Isentropic Flow Equation (Kappa Upwind)

def entropy(T1,p2,p1):
    T2=T1*(p2/p1)**((th.kgas(T1,p1)-1)/(th.kgas(T1,p1)))
    return T2


#Conservation of energy
def energy(T1,v1,p1,T2,p2):
    v2=np.sqrt(2*((0.5*v1**2)+th.hgas(T1,p1)-th.hgas(T2,p2)))
    return v2

#Density

def dens(p2,T2):
    rho2=p2/(th.Rgas()*T2)
    return rho2

#Diameter

def Area(T2,p2,v2,rho2,mdot):
    area=mdot/(rho2*v2)
    return area


def Sim(Pu):
    #Definition of Pressure-Steps and initialisation of Valuedict
    dp=(vs.Pch-Pu)/vs.cells
    #Definition of Initial Conditions
    T1=vs.Tch
    p1=vs.Pch
    v1=vs.vch
    while p1 > 1.01*Pu:
        p2=p1-dp
        T2=entropy(T1,p2,p1)
        v2=energy(T1,v1,p1,T2,p2)
        T1=T2
        p1=p2
        v1=v2
    v2=v2*vs.ispkor
    isp=v2/9.81
    rhoe=dens(p2,T2)
    mdot=vs.Thrust/(v2+(p2-vs.Ps)/(rhoe*v2))#massflow calculated for input thrust at groundlevel (overexpanding engine)
    Ae=Area(T2,p2,v2,rhoe,mdot)
    Fopt=mdot*v2
    print("Engine Simulation Successful")
    return(mdot,isp,Ae,Fopt)