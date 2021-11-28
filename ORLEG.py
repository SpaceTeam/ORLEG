#!/usr/bin/env python3
from inputFiles import parameters
from Engine import Engine
import orSimDataReader
from Tanks import MassObject, GasLiquidTank, GasTank
import orEngineFileWriter


engine = Engine(parameters.name, parameters.fuelType, parameters.fuelTemperature, parameters.oxidizerType, parameters.oxidizerTemperature, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency, parameters.waterFraction)

engineBay = MassObject(mass=1.055, length=0.26, cg=None)
oxTank = GasLiquidTank(tankVolume=2.4*10**-3, tankLength=0.322, tankMass=1.0, liquidType=parameters.oxidizerType, liquidTemperature=parameters.oxidizerTemperature, gasType='Nitrogen', gasTemperature=240, fillLevel=0.95, tankPressure=parameters.oxidizerTankPressure)
oxPress = MassObject(mass=0.4, length=0.104)
oxPressTank = GasTank(tankVolume=0.8*10**-3, tankLength=0.2, tankMass=0.7, gasTemperature=parameters.oxidizerPressurantTemperature, gasType='Nitrogen', tankPressure=parameters.oxidizerPressurantTankPressure)
fuelTank = GasLiquidTank(tankVolume=0.9*10**-3, tankLength=0.18, tankMass=0.4, liquidType=parameters.fuelType, liquidTemperature=parameters.fuelTemperature, gasType='Nitrogen', gasTemperature=250, fillLevel=0.98, tankPressure=parameters.fuelTankPressure)
fuelPress = MassObject(mass=0.17, length=0.09)
fuelPressTank = GasTank(tankVolume=0.25*10**-3, tankLength=0.2, tankMass=0.34, gasTemperature=parameters.fuelPressurantTemperature, gasType='Nitrogen', tankPressure=parameters.fuelPressurantTankPressure)

componentList = [engineBay, oxTank, oxPress, oxPressTank, fuelTank, fuelPress, fuelPressTank]

propulsionSystemLength = MassObject.calculateTotalLength(componentList)
dryMass = MassObject.calculateTotalDryMass(componentList)
wetMass = MassObject.calculateTotalMass(componentList)

fuelVolumeFlowRate = engine.fuelMassFlowRate / fuelTank.liquidDensity
oxidizerVolumeFlowRate = engine.oxMassFlowRate / oxTank.liquidDensity

engine.printParameters()
print("    fuelVolumeFlow: " + str(round(fuelVolumeFlowRate * 1e6, 1)) + " ml/s")
print("    oxidizerVolumeFlow: " + str(round(oxidizerVolumeFlowRate * 1e6, 1)) + " ml/s")
print("Propulsion System Parameters:")
print("    Oxidizer mass: " + str(round(oxTank.liquidMass, 3)) + ' kg')
print("    Fuel mass: " + str(round(fuelTank.liquidMass, 3)) + ' kg')
print("    Oxidizer density: " + str(round(oxTank.liquidDensity, 1)) + ' kg/m³')
print("    Fuel density: " + str(round(fuelTank.liquidDensity, 1)) + ' kg/m³')
print("    Pressurant mass: " + str(round(oxPressTank.gasMass + fuelPressTank.gasMass + oxTank.gasMass + fuelTank.gasMass, 3)) + ' kg')
print("    Structural mass: " + str(round(MassObject.calculateTotalStructuralMass(componentList), 3)) + ' kg')
print("    Dry mass: " + str(round(dryMass, 3)) + ' kg')
print("    Wet mass: " + str(round(wetMass, 3)) + ' kg')
print("    Length: " + str(round(propulsionSystemLength, 3)) + ' m')


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
		thrust = engine.getThrust(ambientPressureList[i] * 1e5)
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
