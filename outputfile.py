# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 16:18:42 2018

@author: Alexx
"""

import numpy as np
import scipy as sp
from CoolProp.CoolProp import PropsSI as ps
import inputfile as vs
import engine as eng
import Datainput as di
import matplotlib.pyplot as plt
import thrustcgfitter as tg

def output(mdot,isp,Thav,Thmax,ltot,mtot,mdry,tlist,cglist,thrustlist,masslist):
    file=open(vs.outputfile,"w").close()
    file=open(vs.outputfile,"w")
    file.write('<engine-database>\n  <engine-list>\n')
    file.write('    <engine  mfg="'+str(vs.Prod)+'" code="'+str(vs.Enginename)+'" Type="Liquid" dia="'+str(int(vs.Ddis*1000))+'" len="'+str(int(ltot*1000))+'" initWt="'+str(int(mtot*1000))+'" propWt="'+str(int((mtot-mdry)*1000))+'" delays="0" auto-calc-mass="'+str(vs.am)+'" auto-calc-cg="0" avgThrust="'+str(Thav)+'" peakThrust="'+str(Thmax)+'" throatDia="0" exitDia="'+str(0*1000)+'" Itot="'+str((mdot*vs.burntime)*isp*9.81)+'" burn-time="'+str(vs.burntime)+'" massFrac="0" Isp="'+str(isp)+'" tDiv="10" tStep="-1." tFix="1" FDiv="10" FStep="-1." FFix="1" mDiv="10" mStep="-1." mFix="1" cgDiv="10" cgStep="-1." cgFix="1">')
    file.write('\n      <data>')
    for n,i in enumerate(tlist):
        file.write('\n        <eng-data cg="'+str(cglist[n]*1000)+'" f="'+str(thrustlist[n])+'" m="'+str(masslist[n])+'" t="'+str(tlist[n])+'"/>')
    file.write('\n      </data>')
    file.write('\n    </engine>')
    file.write('\n  </engine-list>')
    file.write('\n</engine-database>')
    file.close()
    print("File Generation Complete")

pval,tlist,plist=di.dataprocesser()
mdot,isp,area,fopt=eng.Sim(pval)
thrl,thra,thrm=tg.acthrust(pval,plist,fopt,area)
cgl,mlist,ltot,ml,mdry=tg.tanks(mdot,tlist)
val=output(mdot,isp,thra,thrm,ltot,ml,mdry,tlist,cgl,thrl,mlist)
