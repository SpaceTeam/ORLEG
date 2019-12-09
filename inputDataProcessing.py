from inputFiles import parameters
import ceaDataReader as cd
import numpy as np
from CoolProp.CoolProp import PropsSI as ps


# Calculation of fuel tank mass per length TODO: implement diy aluminium tanks
def calculateTankMassPerLength(d):
	wvref = parameters.mtlref / parameters.rhoc
	twref = (parameters.dtref / 2) - np.sqrt(((parameters.dtref * 0.5) ** 2) - wvref / np.pi)
	ws = parameters.Ptanko * parameters.dtref / (2 * twref)
	t = parameters.Ptanko * d / (2 * ws)
	Dt = d + 2 * t
	A = np.pi * ((Dt / 2) ** 2 - (d / 2) ** 2)
	mtl = A * parameters.rhoc
	return mtl


# Check if the sum of the exhaust gas fraction is close enough to 1
def checkExhaustComposition():
	count = 0
	for key in parameters.sw:
		count += parameters.sw[key]
	if not 1 + 0.008 > count > 1 - 0.008:
		print('NOTE! derivation of exhaust fraction from one out of boundaries!', count)


# If required, convert exhaust composition from mole to mass fractions
def convertMoleToMass():
	if parameters.ratioflag == 'mass':
		print('Conversion Complete! Input Parameters=', parameters.ratioflag)
	elif parameters.ratioflag == 'mole':
		mm = 0
		for key in parameters.sw:
			mm += parameters.sw[key] * ps('molarmass', 'P', 200, 'T', 200, key)
		for key in parameters.sw:
			parameters.sw[key] = parameters.sw[key] * ps('molarmass', 'P', 200, 'T', 200, key) / mm
		print('Conversion Complete! Input Parameters=', parameters.ratioflag)
	else:
		print("ERROR! Wrong Conversion Input")


def processInputData():
	if parameters.datainput == 'F':
		parameters.Tch, parameters.sw, parameters.Pch = cd.readCea(parameters.ceainput)
	elif parameters.datainput == 'M':
		None
	else:
		print('invalid value for "datainput"')

	checkExhaustComposition()
	convertMoleToMass()
	return calculateTankMassPerLength(parameters.dt)
