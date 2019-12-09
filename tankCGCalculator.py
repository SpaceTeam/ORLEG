from inputFiles import parameters
import numpy as np
from CoolProp.CoolProp import PropsSI as ps


# Calculation of fuel tank mass per length TODO: implement diy aluminium tanks
def calculateTankMassPerLength(d):
	wvref = parameters.refTankMassPerLength / parameters.densityCarbon
	twref = (parameters.referenceTankDiameter / 2) - np.sqrt(((parameters.referenceTankDiameter * 0.5) ** 2) - wvref / np.pi)
	ws = parameters.oxidizerTankPressure * parameters.referenceTankDiameter / (2 * twref)
	t = parameters.oxidizerTankPressure * d / (2 * ws)
	Dt = d + 2 * t
	A = np.pi * ((Dt / 2) ** 2 - (d / 2) ** 2)
	mtl = A * parameters.densityCarbon
	return mtl


def calculateTankCG(propellantMassFlowRate, timestampList):
	tankMassPerLength = calculateTankMassPerLength(parameters.tankDiameter)
	cgList = []
	propellantMassList = []
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
	print("Fuel tank length: " + str(fuelTankLength) + "m oxidizer tank length: " + str(oxidizerTankLength) + "m")
	oxidizerTankDryMass = oxidizerTankLength * tankMassPerLength  # Oxidizer Tank Dry Mass
	fuelTankDryMass = fuelTankLength * tankMassPerLength  # Fuel Tank Dry Mass
	if parameters.deadOxidizerState == 'l':  # Definition of Dead Mass Distribution (Even for gaseous, bottom for fluid)
		usableOxidizerMassLaunch = totalOxidizerMassLaunch
	elif parameters.deadOxidizerState == 'g':
		oxidizerTankDryMass += oxidizerDeadMass
	else:
		print('cox input error')
	if parameters.deadFuelState == 'l':
		usableFuelMassLaunch = totalFuelMassLaunch
	elif parameters.deadFuelState == 'g':
		fuelTankDryMass += fuelDeadMass
	else:
		print('cf input error')
	distance = 0  # Calculation of Dry Mass CG
	cgFraction = 0
	dryMass = 0
	caf = 1
	cao = 1
	for n, i in enumerate(parameters.massArrangement):
		if i == 'O':
			vmass = oxidizerTankDryMass
			vlength = oxidizerTankLength
			vlox = distance  # distance to Oxidizer Tank Bottom
		elif i == 'F':
			vmass = fuelTankDryMass
			vlength = fuelTankLength
			vlf = distance  # distance to Fuel Tank Bottom
		elif i == 'C':  # Calculatin Coax Tank Assembly
			Di = np.sqrt((parameters.tankDiameter ** 2) / (1 + totalFuelVolume / totalOxidizerVolume))
			l = totalOxidizerVolume / (0.25 * np.pi * Di ** 2)
			ma = l * tankMassPerLength
			mi = l * tankMassPerLength(Di)  # FIXME not a function
			mgt = ma + mi
			vmass = mgt
			vlength = l
			vlf = distance
			vlox = distance
			cao = (np.pi * 0.25 * Di ** 2) / tankArea
			caf = ((np.pi) * 0.25 * ((parameters.tankDiameter ** 2) - (Di ** 2))) / tankArea
		else:
			vmass = i
			vlength = parameters.lengthArrangement[n]
		cgFraction += vmass * (distance + vlength * 0.5)
		distance += vlength
		dryMass += vmass
	tankLength = distance  # Total Tank Length
	wetMass = dryMass + usableOxidizerMassLaunch + usableFuelMassLaunch
	for i in timestampList:  # Generation of propellant mass list during operation
		propellantMassList.append((wetMass - i * propellantMassFlowRate) * 1000)
	cgdry = cgFraction / dryMass
	for i in timestampList:  # Calculation of CG shift during operation
		oxidizerMassCurrent = usableOxidizerMassLaunch - i * oxidizerMassFlowRate
		lsox = (oxidizerMassCurrent / oxidizerDensity) / (tankArea * cao)
		fuelMassCurrent = usableFuelMassLaunch - i * fuelMassFlowRate
		lsf = (fuelMassCurrent / fuelDensity) / (tankArea * caf)
		cgFraction = dryMass * cgdry + oxidizerMassCurrent * (vlox + lsox * 0.5) + fuelMassCurrent * (vlf + lsf * 0.5)
		totalMassCurrent = dryMass + oxidizerMassCurrent + fuelMassCurrent
		cgt = tankLength - (cgFraction / totalMassCurrent)
		cgList.append(cgt)
	return cgList, propellantMassList, tankLength, wetMass, dryMass
