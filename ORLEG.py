#!/usr/bin/env python3

from inputFiles import parameters
from Engine import Engine
import orSimDataReader
from Tanks import MassObject, GasLiquidTank, GasTank
import orEngineFileWriter


engine = Engine(parameters.name, parameters.fuelType, parameters.oxidizerType, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency, parameters.waterFraction)
engine.printParameters()

engineBay = MassObject(mass=1.9, length=0.14, cg=0)
oxTank = GasLiquidTank(tankVolume=2.04*10**-3, tankLength=0.34, tankMass=1.05, liquidType=parameters.oxidizerType, liquidTemperature=parameters.oxidizerTemperature, gasType='Nitrogen', gasTemperature=240, fillLevel=0.90, tankPressure=parameters.oxidizerTankPressure)
oxPress = MassObject(mass=0.3, length=0.16)
oxPressTank = GasTank(tankVolume=0.8*10**-3, tankLength=0.2, tankMass=0.7, gasTemperature=293, gasType='Nitrogen', tankPressure=250*10**5)
fuelTank = GasLiquidTank(tankVolume=0.73*10**-3, tankLength=0.10, tankMass=0.4, liquidType=parameters.fuelType, liquidTemperature=parameters.fuelTemperature, gasType='Nitrogen', gasTemperature=250, fillLevel=0.95, tankPressure= parameters.fuelTankPressure)
fuelPress = MassObject(mass=0.3, length=0.16)
fuelPressTank = GasTank(tankVolume=0.25*10**-3, tankLength=0.2, tankMass=0.34, gasTemperature=293, gasType='Nitrogen', tankPressure=250*10**5)

componentList = [engineBay, oxTank, oxPress, oxPressTank, fuelTank, fuelPress, fuelPressTank]

propulsionSystemLength = MassObject.calculateTotalLength(componentList)
dryMass = MassObject.calculateTotalDryMass(componentList)
wetMass = MassObject.calculateTotalMass(componentList)

print("")
print("Propulsion System Parameters:")
print("    Oxidizer mass: " + str(round(oxTank.liquidMass, 3)))
print("    Fuel mass: " + str(round(fuelTank.liquidMass, 3)))
print("    Pressurant mass: " + str(round(oxPressTank.gasMass + fuelPressTank.gasMass + oxTank.gasMass + fuelTank.gasMass, 3)))
print("    Structural mass: " + str(round(MassObject.calculateTotalStructuralMass(componentList), 3)))
print("    Dry mass: " + str(round(dryMass, 3)))
print("    Wet mass: " + str(round(wetMass, 3)))
print("    Length: " + str(round(propulsionSystemLength, 3)))


timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(parameters.orDataFileName, parameters.maxBurnDuration, parameters.orDataReductionFactor)

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
	burnedFuelMass, flownPressurantMass = fuelTank.removeLiquidMassKeepTankPressure(fuelMassToBurn)
	fuelPressTank.addGasMass(-flownPressurantMass)
	oxidizerMassToBurn = engine.oxMassFlowRate * timestep
	burnedOxMass, flownPressurantMass = oxTank.removeLiquidMassKeepTankPressure(oxidizerMassToBurn)
	oxPressTank.addGasMass(-flownPressurantMass)

	massList.append(MassObject.calculateTotalMass(componentList))
	cgList.append(propulsionSystemLength - MassObject.calculateTotalCG(componentList))

	if burnedFuelMass < fuelMassToBurn or burnedOxMass < oxidizerMassToBurn:
		thrust = 0
		if burnTime is None:
			burnTime = timestampList[i]
			print("\nburnout at t=" + str(round(burnTime, 2)) + ", remaining fuel mass: " + str(round(fuelTank.getLiquidMass() * 1000, 1)) + "g, remaining oxidizer mass: " + str(round(oxTank.getLiquidMass() * 1000, 1)) + "g")
	else:
		thrust = engine.getThrust(ambientPressureList[i] * 10**5)
		thrustNum += 1

	thrustList.append(thrust)
	thrustSum += thrust
	if thrust > maxThrust:
		maxThrust = thrust
avgThrust = thrustSum / thrustNum

if burnTime is None:
	burnTime = parameters.maxBurnDuration
	print("\nmax. burn time reached, remaining fuel mass: " + str(round(fuelTank.getLiquidMass() * 1000, 1)) + "g, remaining oxidizer mass: " + str(round(oxTank.getLiquidMass() * 1000, 1)) + "g")

orEngineFileWriter.writeEngineFile(burnTime, avgThrust, maxThrust, propulsionSystemLength, wetMass, dryMass, timestampList, cgList, thrustList, massList)
