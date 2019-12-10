#!/usr/bin/env python3

import inputDataProcessing
import orSimDataReader
import engineSim
import tankCGCalculator
import orEngineFileWriter


inputDataProcessing.processInputData()
refAmbientPressure, timestampList, ambientPressureList = orSimDataReader.readORSimData()
massFlowRate, specificImpulse, exitArea, refThrust = engineSim.simulateEngine(refAmbientPressure)
thrustList, averageThrust, maximumThrust = engineSim.calcThrustAltComp(refAmbientPressure, ambientPressureList, refThrust, exitArea)
cgList, propellantMassList, tankLength, wetMass, dryMass = tankCGCalculator.calculateTankCG(massFlowRate, timestampList)
orEngineFileWriter.writeEngineFile(massFlowRate, specificImpulse, averageThrust, maximumThrust, tankLength, wetMass, dryMass, timestampList, cgList, thrustList, propellantMassList)
