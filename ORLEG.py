#!/usr/bin/env python3

from inputFiles import parameters
from Engine import Engine
import orSimDataReader
import tankCGCalculator
from Tanks import MassObject
from Tanks import Tank
import orEngineFileWriter

engineBay = MassObject(1.7, 0.14, 0)
oxTank = Tank(2.04*10**-3, 0.32, 1.02, parameters.oxidizerType, parameters.oxidizerTankTemperature, 'Nitrogen', 273, 0.95, 45*10**5)
oxPress = MassObject(0.26, 0.25)
oxPressTank = Tank(0.8*10**-3, 0.2, 0.59, 'Water', 293, 'Nitrogen', 283, 0, 250*10**5)
fuelTank = Tank(0.73*10**-3, 0.12, 0.32, parameters.fuelType, parameters.fuelTankTemperature, 'Nitrogen', 273, 0.95, 30*10**5)
fuelPress = MassObject(0.25, 0.25)
fuelPressTank = Tank(0.25*10**-3, 0.2, 0.285, 'Water', 293, 'Nitrogen', 283, 0, 250*10**5)

componentList = [engineBay, oxTank, oxPress, oxPressTank, fuelTank, fuelPress, fuelPressTank]

print(oxTank.fluidMass)
print(fuelTank.fluidMass)
print(oxPressTank.pressurantMass + fuelPressTank.pressurantMass + oxTank.pressurantMass + fuelTank.pressurantMass)
print(MassObject.calculateTotalMass(componentList))
print(MassObject.calculateTotalCG(componentList))

engine = Engine(parameters.name, parameters.fuelType, parameters.oxidizerType, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency, parameters.waterFraction)
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
