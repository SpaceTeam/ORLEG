#!/usr/bin/env python3

import inputDataProcessing
import orSimDataReader
import engineSim
import tankCGCalculator
import orEngineFileWriter


mpl = inputDataProcessing.processInputData()
pval, tlist, plist = orSimDataReader.readORSimData()
mdot, isp, area, fopt = engineSim.simulate(pval)
thrl, thra, thrm = engineSim.calcThrustAltComp(pval, plist, fopt, area)
cgl, mlist, ltot, ml, mdry = tankCGCalculator.calculateTankCG(mdot, tlist, mpl)
orEngineFileWriter.writeEngineFile(mdot, isp, thra, thrm, ltot, ml, mdry, tlist, cgl, thrl, mlist)
