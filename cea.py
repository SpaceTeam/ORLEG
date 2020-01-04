from inputFiles import parameters
from CoolProp.CoolProp import PropsSI

acceptanceList = ['CO', 'CO2', 'H2', 'H2O', 'O2', 'H2', 'N2']

chamberTemperature = None
chamberPressure = None
exhaustComposition = None


def readCea(filename):
	with open(filename, "r") as file:
		switch = 0
		compdict = {}
		for line in file:
			a = line.split()
			b = len(a)
			if b > 2:
				if a[0] == 'T,' and a[1] == 'K':
					Tcomb = float(a[2])
				elif a[0] == 'P,' and a[1] == 'BAR':
					Pcomb = float(a[2]) * 10 ** 5
			if switch > 0:
				switch += 1
				if b > 1:
					sname = a[0]
					sname = sname.strip('*')
					for i in acceptanceList:
						if sname == i:
							sval = a[1]
							sval = float(sval.replace('-', 'e-'))
							compdict[sname] = sval
				else:
					if switch > 4:
						switch = 0
						break
			if b == 2:
				if a[0] == 'MOLE' and a[1] == 'FRACTIONS':
					switch = 1
	return Tcomb, Pcomb, compdict


# Check if the sum of the exhaust gas fraction is close enough to 1
def checkExhaustComposition():
	fractionSum = 0
	for key in exhaustComposition:
		fractionSum += exhaustComposition[key]
	if abs(fractionSum - 1) > 0.01:
		print('WARNING! exhaust fraction sum out of boundaries:', fractionSum)


# If required, convert exhaust composition from mole to mass fractions
def convertMoleToMass():
	if parameters.exhaustCompositionRatioType == 'mass':
		pass
	elif parameters.exhaustCompositionRatioType == 'mole':
		molarMassSum = 0
		for key in exhaustComposition:
			molarMassSum += exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key)
		for key in exhaustComposition:
			exhaustComposition[key] = exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key) / molarMassSum
	else:
		print('ERROR! Invalid setting for parameter exhaustCompositionRatioType')


# Process input data, calls functions above
def getCeaData():
	global chamberTemperature, chamberPressure, exhaustComposition
	chamberTemperature, chamberPressure, exhaustComposition = readCea(parameters.ceaDataFileName)
	checkExhaustComposition()
	convertMoleToMass()
	return chamberTemperature, chamberPressure, exhaustComposition
