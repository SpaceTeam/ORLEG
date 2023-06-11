#!/usr/bin/env python3
from inputFiles import parameters
from Engine import Engine
import orSimDataReader
from Tanks import MassObject, GasLiquidTank, GasTank
import orEngineFileWriter
import math
import matplotlib.pyplot as plt


engine = Engine(parameters.name, parameters.fuelType, parameters.fuelTemperature, parameters.oxidizerType, parameters.oxidizerTemperature, parameters.oxidizerFuelRatio, parameters.chamberPressure, parameters.referenceAmbientPressure, parameters.referenceThrust, parameters.engineEfficiency, parameters.waterFraction)

diameter = 0.130

oxTankVolume = 4.4e-3			   # e-3m^3  ... liter
oxTanklength = oxTankVolume / (math.pi * (diameter/2)**2)
print("oxTanklength: " + str(oxTanklength) + "m")
#oxPressTankVolume = 1.1e-3   # 5.2liter
#oxPressTanklength = oxPressTankVolume / (math.pi * (diameter/2)**2)
oxPressTankVolume = 1.1e-3  		# e-3m^3  ... liter
oxPressTanklength = 0.279
oxPressTankMass = 0.65

fuelTankVolume = 4.7e-3				# e-3m^3  ... liter
fuelTankLength = fuelTankVolume / (math.pi * (diameter/2)**2)
print("fuelTankLength: " + str(fuelTankLength) + "m")

#fuelPressTankVolume = 1.0e-3		#4.0liter
#fuelPressTankLength = fuelPressTankVolume / (math.pi * (diameter/2)**2)

fuelPressTankVolume = 1.1e-3		# e-3m^3  ... liter
fuelPressTankLength = 0.279
fuelPressTankMass = 0.65

engineBay = MassObject(mass=1.680, length=0.294, cg=0.150)
oxTank = GasLiquidTank(tankVolume=oxTankVolume, tankLength=oxTanklength, tankMass=1.0, liquidType=parameters.oxidizerType, liquidTemperature=parameters.oxidizerTemperature, gasType='O2', gasTemperature=240, fillLevel=0.95, tankPressure=parameters.oxidizerTankPressure)  # Aluminium
#oxTank = GasLiquidTank(tankVolume=2400e-6, tankLength=0.387, tankMass=1.925, liquidType=parameters.oxidizerType, liquidTemperature=parameters.oxidizerTemperature, gasType='Nitrogen', gasTemperature=240, fillLevel=0.95, tankPressure=parameters.oxidizerTankPressure)  # Steel
oxPress = MassObject(mass=0.6, length=0.1)
oxPressTank = GasTank(tankVolume=oxPressTankVolume, tankLength=oxPressTanklength, tankMass=oxPressTankMass, gasTemperature=parameters.oxidizerPressurantTemperature, gasType='Nitrogen', tankPressure=parameters.oxidizerPressurantTankPressure)
fuelTank = GasLiquidTank(tankVolume=fuelTankVolume, tankLength=fuelTankLength, tankMass=1.0, liquidType=parameters.fuelType, liquidTemperature=parameters.fuelTemperature, gasType='Nitrogen', gasTemperature=250, fillLevel=0.99, tankPressure=parameters.fuelTankPressure)  # Aluminium
#fuelTank = GasLiquidTank(tankVolume=900e-6, tankLength=0.192, tankMass=0.876, liquidType=parameters.fuelType, liquidTemperature=parameters.fuelTemperature, gasType='Nitrogen', gasTemperature=250, fillLevel=0.5, tankPressure=parameters.fuelTankPressure)  # Steel
fuelPress = MassObject(mass=0.6, length=0.1)
fuelPressTank = GasTank(tankVolume=fuelPressTankVolume, tankLength=fuelPressTankLength, tankMass=fuelPressTankMass, gasTemperature=parameters.fuelPressurantTemperature, gasType='Nitrogen', tankPressure=parameters.fuelPressurantTankPressure)

componentList = [engineBay, fuelTank, fuelPress, fuelPressTank, oxTank, oxPress, oxPressTank]

propulsionSystemLength = MassObject.calculateTotalLength(componentList)
dryMass = MassObject.calculateTotalDryMass(componentList)
wetMass = MassObject.calculateTotalMass(componentList)

fuelVolumeFlowRate = engine.fuelMassFlowRate / fuelTank.liquidDensity
oxidizerVolumeFlowRate = engine.oxMassFlowRate / oxTank.liquidDensity

engine.printParameters()
print("    fuelVolumeFlow: " + str(round(fuelVolumeFlowRate * 1e6, 1)) + " ml/s")
print("    oxidizerVolumeFlow: " + str(round(oxidizerVolumeFlowRate * 1e6, 1)) + " ml/s")
print("Propulsion System Parameters:")
print("    Ox Pressurant mass: " + str(round(oxPressTank.gasMass, 3)) + ' kg')
print("    Ox Pressurant Gas mass: " + str(round(oxTank.gasMass, 3)) + ' kg')
print("    Oxidizer mass: " + str(round(oxTank.liquidMass, 3)) + ' kg')
print("    Fuel Pressurant mass: " + str(round(fuelPressTank.gasMass, 3)) + ' kg')
print("    Fuel Pressurant Gas mass: " + str(round(fuelTank.gasMass, 3)) + ' kg')
print("    Fuel mass: " + str(round(fuelTank.liquidMass, 3)) + ' kg')
print("    Oxidizer density: " + str(round(oxTank.liquidDensity, 1)) + ' kg/m³')
print("    Fuel density: " + str(round(fuelTank.liquidDensity, 1)) + ' kg/m³')
print("    Structural mass: " + str(round(MassObject.calculateTotalStructuralMass(componentList), 3)) + ' kg')
print("    Dry mass: " + str(round(dryMass, 3)) + ' kg')
print("    Wet mass: " + str(round(wetMass, 3)) + ' kg')
print("    Propellant mass: " + str(round(wetMass-dryMass, 3)) + ' kg')
print("    Length: " + str(round(propulsionSystemLength, 3)) + ' m')


timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(parameters.orDataFileName, parameters.maxBurnDuration, parameters.orDataReductionFactor)

burnTime = None
thrustList = []

oxpressMassList = []
oxMassList = []
fuelpressMassList = []
fuelMassList = []

index_of_end = 0

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

	fuelpressMassList.append(flownPressurantMass/timestep)
	fuelMassList.append(burnedFuelMass/timestep)

	oxidizerMassToBurn = engine.oxMassFlowRate * timestep
	burnedOxMass, flownPressurantMass = oxTank.removeLiquidMassKeepTankPressure(oxidizerMassToBurn)
	oxPressTank.addGasMass(-flownPressurantMass)

	oxpressMassList.append(flownPressurantMass/timestep)
	oxMassList.append(burnedFuelMass/timestep)


	massList.append(MassObject.calculateTotalMass(componentList))
	cgList.append(propulsionSystemLength - MassObject.calculateTotalCG(componentList))

	oxPressTankEmpty = oxPressTank.getTankPressure() < (oxTank.getTankPressure() + parameters.oxidizerPressHeadPressure)
	fuelPressTankEmpty = fuelPressTank.getTankPressure() < (fuelTank.getTankPressure() + parameters.fuelPressHeadPressure)

	if burnedFuelMass < fuelMassToBurn or burnedOxMass < oxidizerMassToBurn or oxPressTankEmpty or fuelPressTankEmpty:
		thrust = 0
		if burnTime is None:			
			burnTime = timestampList[i]
			index_of_end = i - 1
			ox_press_string = "oxPressTank pressure: " + str(round(oxPressTank.getTankPressure() * 1e-5, 1)) + "bar" if not oxPressTankEmpty else "oxPressTank pressure: empty"
			fuel_press_string = "fuelPressTank pressure: " + str(round(fuelPressTank.getTankPressure() * 1e-5, 1)) + "bar" if not fuelPressTankEmpty else "fuelPressTank pressure: empty"
			print("\nburnout at t=" + str(round(burnTime, 2)) + ", remaining fuel mass: " + str(round(fuelTank.getLiquidMass() * 1000, 1)) + "g, remaining oxidizer mass: " + str(round(oxTank.getLiquidMass() * 1000, 1)) + "g, " + ox_press_string + ", " + fuel_press_string)
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

del timestampList[index_of_end:]
del oxpressMassList[index_of_end:]
del oxMassList[index_of_end:]
del fuelpressMassList[index_of_end:]
del fuelMassList[index_of_end:]
del massList[index_of_end:]
del cgList[index_of_end:]
del thrustList[index_of_end:]


del timestampList[:1]
del oxpressMassList[:1]
del oxMassList[:1]
del fuelpressMassList[:1]
del fuelMassList[:1]
del massList[:1]
del cgList[:1]
del thrustList[:1]

plt.plot(timestampList, oxpressMassList)
plt.plot(timestampList, oxMassList)
plt.show()
plt.plot(timestampList, fuelpressMassList)
plt.plot(timestampList, fuelMassList)
plt.show()

plt.plot(timestampList, thrustList)
plt.show()
plt.plot(timestampList, massList)
plt.show()

orEngineFileWriter.writeMassflowFile('ox_pressurant', burnTime, timestampList, oxpressMassList)
orEngineFileWriter.writeMassflowFile('ox', burnTime, timestampList, oxMassList)
orEngineFileWriter.writeMassflowFile('fuel_pressurant', burnTime, timestampList, fuelpressMassList)
orEngineFileWriter.writeMassflowFile('fuel', burnTime, timestampList, fuelMassList)

orEngineFileWriter.writeMassflowFile('thrust', burnTime, timestampList, thrustList)

orEngineFileWriter.writeEngineFile(burnTime, avgThrust, maxThrust, propulsionSystemLength, wetMass, dryMass, timestampList, cgList, thrustList, massList)

plt.plot(timestampList, cgList)
plt.show()