from inputFiles import parameters
import numpy as np
from CoolProp.CoolProp import PropsSI as ps


# Calculation of propellant tank mass
def calculateTankMass(tankDiameter, tankLength, tankPressure):
	if parameters.tankType == 'c':  # calculate carbon tank mass using Barlow's formula (Kesselformel), maximum tension calculated from reference tank, endcap mass ignored
		# calculate maximum tension in reference tank wall
		referenceWallArea = parameters.referenceCarbonTankMassPerLength / parameters.carbonDensity
		referenceTankRadius = parameters.referenceCarbonTankDiameter / 2
		referenceWallThickness = referenceTankRadius - np.sqrt((referenceTankRadius ** 2) - referenceWallArea / np.pi)
		maximumTension = tankPressure * parameters.referenceCarbonTankDiameter / (2 * referenceWallThickness)
		# calculate tank mass
		wallThickness = tankPressure * tankDiameter / (2 * maximumTension)
		outerDiameter = tankDiameter + 2 * wallThickness
		wallArea = np.pi * ((outerDiameter / 2) ** 2 - (tankDiameter / 2) ** 2)
		massPerLength = wallArea * parameters.carbonDensity
		return massPerLength * tankLength
	elif parameters.tankType == 'a':  # calculate aluminium tank mass using Barlow's formula (Kesselformel)
		wallThickness = tankPressure * tankDiameter / (2 * parameters.aluminiumYieldStrength)
		wallThickness *= parameters.aluminiumTankSafetyFactor
		if wallThickness < parameters.aluminiumTankMinWallThickness:
			wallThickness = parameters.aluminiumTankMinWallThickness
		outerDiameter = tankDiameter + 2 * wallThickness
		wallArea = np.pi * ((outerDiameter / 2) ** 2 - (tankDiameter / 2) ** 2)
		massPerLength = wallArea * parameters.aluminiumDensity
		return massPerLength * tankLength + 2 * parameters.aluminiumTankEndcapMass
	else:
		print('ERROR! Invalid setting for parameter tankType')


def calculateTankCG(propellantMassFlowRate, timestampList):
	usablePropellantMassLaunch = propellantMassFlowRate * parameters.burnDuration  # Operational Propellant Mass
	usableOxidizerMassLaunch = usablePropellantMassLaunch * (parameters.oxidizerFuelRatio / (1 + parameters.oxidizerFuelRatio))  # Usable Oxidizer Mass
	oxidizerMassFlowRate = propellantMassFlowRate * (parameters.oxidizerFuelRatio / (1 + parameters.oxidizerFuelRatio))  # Oxidizer Massflow
	usableFuelMassLaunch = usablePropellantMassLaunch - usableOxidizerMassLaunch  # Usable Fuel Mass
	fuelMassFlowRate = propellantMassFlowRate - oxidizerMassFlowRate  # Fuel Mass Flow
	totalOxidizerMassLaunch = usableOxidizerMassLaunch * (1 + parameters.deadOxidizerMassFraction)  # Total Oxidizer Mass
	oxidizerDeadMass = totalOxidizerMassLaunch - usableOxidizerMassLaunch  # Oxidizer Dead Mass
	totalFuelMassLaunch = usableFuelMassLaunch * (1 + parameters.deadFuelMassFraction)  # Total Fuel Mass
	fuelDeadMass = totalFuelMassLaunch - usableFuelMassLaunch  # Fuel Dead Mass
	oxidizerDensity = ps('D', 'Q', parameters.oxidizerTankGasFraction, 'T', parameters.oxidizerTankTemperature, parameters.oxidizerType)  # Oxidizer Density
	fuelDensity = ps('D', 'P', parameters.fuelTankPressure, 'T', parameters.fuelTankTemperature, parameters.fuelType)  # Fuel Density
	tankArea = 0.25 * np.pi * parameters.tankDiameter ** 2  # Tank Area
	totalOxidizerVolume = totalOxidizerMassLaunch / oxidizerDensity  # Total Oxidizer Volume
	totalFuelVolume = totalFuelMassLaunch / fuelDensity  # Total Fuel Volume
	oxidizerTankLength = totalOxidizerVolume / tankArea  # Oxidizer Tank Length
	fuelTankLength = totalFuelVolume / tankArea  # Fuel Tank Length
	oxidizerTankDryMass = calculateTankMass(parameters.tankDiameter, oxidizerTankLength, parameters.oxidizerTankPressure)  # Oxidizer Tank Dry Mass
	fuelTankDryMass = calculateTankMass(parameters.tankDiameter, fuelTankLength, parameters.fuelTankPressure)  # Fuel Tank Dry Mass
	print("oxidizer tank length in m: " + str(oxidizerTankLength) + ", dry mass in kg: " + str(oxidizerTankDryMass))
	print("fuel tank length in m: " + str(fuelTankLength) + ", dry mass in kg: " + str(fuelTankDryMass))

	# Definition of Dead Mass Distribution (Even for gaseous, bottom for fluid)
	if parameters.deadOxidizerState == 'l':
		usableOxidizerMassLaunch = totalOxidizerMassLaunch
	elif parameters.deadOxidizerState == 'g':
		oxidizerTankDryMass += oxidizerDeadMass
	else:
		print('ERROR! Invalid setting for parameter deadOxidizerState')
	if parameters.deadFuelState == 'l':
		usableFuelMassLaunch = totalFuelMassLaunch
	elif parameters.deadFuelState == 'g':
		fuelTankDryMass += fuelDeadMass
	else:
		print('ERROR! Invalid setting for parameter deadFuelState')

	# Calculation of Dry Mass CG
	distance = 0
	distanceToOxidizerTankBottom = 0
	distanceToFuelTankBottom = 0
	cgFraction = 0
	dryMass = 0
	fuelTankVolumeCorrectionFactor = 1
	oxidizerTankVolumeCorrectionFactor = 1
	for n, i in enumerate(parameters.massArrangement):
		if i == 'O':
			tankSectionMass = oxidizerTankDryMass
			tankSectionLength = oxidizerTankLength
			distanceToOxidizerTankBottom = distance  # distance to Oxidizer Tank Bottom
		elif i == 'F':
			tankSectionMass = fuelTankDryMass
			tankSectionLength = fuelTankLength
			distanceToFuelTankBottom = distance  # distance to Fuel Tank Bottom
		elif i == 'C':  # Coax Tank Assembly
			innerTankDiameter = np.sqrt((parameters.tankDiameter ** 2) / (1 + totalFuelVolume / totalOxidizerVolume))
			tankLength = totalOxidizerVolume / (0.25 * np.pi * innerTankDiameter ** 2)
			outerTankMass = calculateTankMass(parameters.tankDiameter, tankLength, parameters.fuelTankPressure)  # FIXME assumes fuel tank on outside
			innerTankMass = calculateTankMass(innerTankDiameter, tankLength, parameters.oxidizerTankPressure)  # FIXME assumes oxidizer tank on inside
			tankSectionMass = outerTankMass + innerTankMass
			tankSectionLength = tankLength
			distanceToFuelTankBottom = distance
			distanceToOxidizerTankBottom = distance
			oxidizerTankVolumeCorrectionFactor = (np.pi * 0.25 * innerTankDiameter ** 2) / tankArea
			fuelTankVolumeCorrectionFactor = (np.pi * 0.25 * ((parameters.tankDiameter ** 2) - (innerTankDiameter ** 2))) / tankArea
		else:
			tankSectionMass = i
			tankSectionLength = parameters.lengthArrangement[n]
		cgFraction += tankSectionMass * (distance + tankSectionLength * 0.5)
		distance += tankSectionLength
		dryMass += tankSectionMass
	tankLength = distance  # Total Tank Length
	wetMass = dryMass + usableOxidizerMassLaunch + usableFuelMassLaunch
	cgDry = cgFraction / dryMass

	# Generation of propellant mass list during operation
	propellantMassList = []
	for timestamp in timestampList:
		propellantMassList.append((wetMass - timestamp * propellantMassFlowRate) * 1000)

	# Calculation of CG shift during operation
	cgList = []
	for timestamp in timestampList:
		oxidizerMassCurrent = usableOxidizerMassLaunch - timestamp * oxidizerMassFlowRate
		oxidizerTankFillState = (oxidizerMassCurrent / oxidizerDensity) / (tankArea * oxidizerTankVolumeCorrectionFactor)
		fuelMassCurrent = usableFuelMassLaunch - timestamp * fuelMassFlowRate
		fuelTankFillState = (fuelMassCurrent / fuelDensity) / (tankArea * fuelTankVolumeCorrectionFactor)
		cgFraction = dryMass * cgDry + oxidizerMassCurrent * (distanceToOxidizerTankBottom + oxidizerTankFillState * 0.5) + fuelMassCurrent * (distanceToFuelTankBottom + fuelTankFillState * 0.5)
		totalMassCurrent = dryMass + oxidizerMassCurrent + fuelMassCurrent
		cgt = tankLength - (cgFraction / totalMassCurrent)
		cgList.append(cgt)
	print("Tank mass and CG calculation done, tankLength: " + str(tankLength) + " dryMass: " + str(dryMass) + " wetMass: " + str(wetMass))
	return cgList, propellantMassList, tankLength, wetMass, dryMass
