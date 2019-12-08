#!/usr/bin/env python3

import orSimDataReader
import engineSim
import thrustCGFitter
import orEngineFileWriter


pval, tlist, plist = orSimDataReader.readORSimData()
mdot, isp, area, fopt = engineSim.simulate(pval)
thrl, thra, thrm = engineSim.calcThrustAltComp(pval, plist, fopt, area)
cgl, mlist, ltot, ml, mdry = thrustCGFitter.tanks(mdot, tlist)
orEngineFileWriter.writeEngineFile(mdot, isp, thra, thrm, ltot, ml, mdry, tlist, cgl, thrl, mlist)
