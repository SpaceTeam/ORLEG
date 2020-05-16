#!/usr/bin/env python3

from inputFiles import parameters
from Engine import Engine
import orSimDataReader
from Tanks import MassObject
from Tanks import Tank
import orEngineFileWriter


engine = Engine(parameters.name, parameters.fuelType, parameters.oxidizerType, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency, parameters.waterFraction)
engine.printParameters()

engineBay = MassObject(1.9, 0.14, 0)
oxTank = Tank(2.04*10**-3, 0.34, 1.05, parameters.oxidizerType, parameters.oxidizerTankTemperature, 'Nitrogen', 240, 0.95, parameters.oxidizerTankPressure)
oxPress = MassObject(0.3, 0.16)
oxPressTank = Tank(0.8*10**-3, 0.2, 0.7, 'Water', 293, 'Nitrogen', 283, 0, 250*10**5)
fuelTank = Tank(0.73*10**-3, 0.10, 0.4, parameters.fuelType, parameters.fuelTankTemperature, 'Nitrogen', 250, 0.95, parameters.fuelTankPressure)
fuelPress = MassObject(0.3, 0.16)
fuelPressTank = Tank(0.25*10**-3, 0.2, 0.34, 'Water', 293, 'Nitrogen', 283, 0, 250*10**5)

componentList = [engineBay, oxTank, oxPress, oxPressTank, fuelTank, fuelPress, fuelPressTank]

propulsionSystemLength = MassObject.calculateTotalLength(componentList)
dryMass = MassObject.calculateTotalDryMass(componentList)
wetMass = MassObject.calculateTotalMass(componentList)

print("")
print("Propulsion System Parameters:")
print("    Oxidizer mass: " + str(round(oxTank.fluidMass, 3)))
print("    Fuel mass: " + str(round(fuelTank.fluidMass, 3)))
print("    Pressurant mass: " + str(round(oxPressTank.pressurantMass + fuelPressTank.pressurantMass + oxTank.pressurantMass + fuelTank.pressurantMass, 3)))
print("    Structural mass: " + str(round(MassObject.calculateTotalStructuralMass(componentList), 3)))
print("    Dry mass: " + str(round(dryMass, 3)))
print("    Wet mass: " + str(round(wetMass, 3)))
print("    Length: " + str(round(propulsionSystemLength, 3)))


timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(parameters.orDataFileName, parameters.burnDuration, parameters.orDataReductionFactor)

burnTime = None
thrustList = []
thrustSum = 0
thrustNum = 0
maxThrust = 0
massList = []
cgList = []

for i in range(len(timestampList)):
	if i == 0:
		timestep = 0
	else:
		timestep = timestampList[i] - timestampList[i - 1]

	fuelMassToBurn = engine.fuelMassFlowRate * timestep
	burnedFuelMass, flownPressurantMass = fuelTank.removeFluidMassKeepTankPressure(fuelMassToBurn)
	fuelPressTank.addPressurantMass(-flownPressurantMass)
	oxidizerMassToBurn = engine.oxMassFlowRate * timestep
	burnedOxMass, flownPressurantMass = oxTank.removeFluidMassKeepTankPressure(oxidizerMassToBurn)
	oxPressTank.addPressurantMass(-flownPressurantMass)

	massList.append(MassObject.calculateTotalMass(componentList))
	cgList.append(propulsionSystemLength - MassObject.calculateTotalCG(componentList))

	if burnedFuelMass < fuelMassToBurn or burnedOxMass < oxidizerMassToBurn:
		thrust = 0
		if burnTime is None:
			burnTime = timestampList[i]
			print("\nearly burnout at t=" + str(round(burnTime, 2)) + ", remaining fuel mass: " + str(round(fuelTank.getFluidMass()*1000, 1)) + "g, remaining oxidizer mass: " + str(round(oxTank.getFluidMass()*1000, 1)) + "g")
	else:
		thrust = engine.getThrust(ambientPressureList[i] * 10**5)
		thrustNum += 1

	thrustList.append(thrust)
	thrustSum += thrust
	if thrust > maxThrust:
		maxThrust = thrust
avgThrust = thrustSum / thrustNum

if burnTime is None:
	burnTime = parameters.burnDuration
	print("\npropellant remaining at burnout, remaining fuel mass: " + str(round(fuelTank.getFluidMass()*1000, 1)) + "g, remaining oxidizer mass: " + str(round(oxTank.getFluidMass()*1000, 1)) + "g")

orEngineFileWriter.writeEngineFile(burnTime, avgThrust, maxThrust, propulsionSystemLength, wetMass, dryMass, timestampList, cgList, thrustList, massList)
