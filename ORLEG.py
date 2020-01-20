#!/usr/bin/env python3

from inputFiles import parameters
from Engine import Engine
import orSimDataReader
import tankCGCalculator
import orEngineFileWriter


engine = Engine(parameters.name, parameters.fuelType, parameters.oxidizerType, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency)
engine.printParameters()

timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(parameters.orDataFileName, parameters.burnDuration, parameters.orDataReductionFactor)

thrustList = []
thrustSum = 0
maxThrust = 0
for ambientPressure in ambientPressureList:
	thrust = engine.thrust(ambientPressure)
	thrustList.append(thrust)
	thrustSum += thrust
	if thrust > maxThrust:
		maxThrust = thrust
avgThrust = thrustSum / len(thrustList)

cgList, propellantMassList, tankLength, wetMass, dryMass = tankCGCalculator.calculateTankCG(engine.massFlowRate, timestampList)

orEngineFileWriter.writeEngineFile(avgThrust, maxThrust, tankLength, wetMass, dryMass, timestampList, cgList, thrustList, propellantMassList)
