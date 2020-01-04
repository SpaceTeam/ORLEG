from inputFiles import parameters
from CoolProp.CoolProp import PropsSI
from rocketcea.cea_obj import CEA_Obj

acceptanceList = ['CO', 'CO2', 'H2', 'H2O', 'O2', 'H2', 'N2']


def extractExhaustComposition(ceaOutput):
	switch = 0
	exhaustComposition = {}
	for line in ceaOutput.splitlines():
		a = line.split()
		b = len(a)
		if switch > 0:
			switch += 1
			if b > 1:
				sname = a[0]
				sname = sname.strip('*')
				for i in acceptanceList:
					if sname == i:
						sval = a[1]
						sval = float(sval.replace('-', 'e-'))
						exhaustComposition[sname] = sval
			else:
				if switch > 4:
					switch = 0
					break
		if b == 2:
			if a[0] == 'MOLE' and a[1] == 'FRACTIONS':
				switch = 1
	return exhaustComposition


# Check if the sum of the exhaust gas fraction is close enough to 1
def checkExhaustComposition(exhaustComposition):
	fractionSum = 0
	for key in exhaustComposition:
		fractionSum += exhaustComposition[key]
	if abs(fractionSum - 1) > 0.01:
		print('WARNING! exhaust fraction sum out of boundaries:', fractionSum)


# If required, convert exhaust composition from mole to mass fractions
def convertMoleToMass(exhaustComposition):
	molarMassSum = 0
	for key in exhaustComposition:
		molarMassSum += exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key)
	for key in exhaustComposition:
		exhaustComposition[key] = exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key) / molarMassSum
	return exhaustComposition


# Process input data, calls functions above
def getCeaData():
	cea = CEA_Obj(oxName=parameters.oxidizerType, fuelName=parameters.fuelType, useSiUnits=True)

	expansionAreaRatio = cea.get_eps_at_PcOvPe(Pc=parameters.chamberPressure, MR=parameters.oxidizerFuelRatio, PcOvPe=parameters.expansionPressureRatio)

	chamberTemperature = cea.get_Tcomb(Pc=parameters.chamberPressure, MR=parameters.oxidizerFuelRatio)

	ceaOutput = cea.get_full_cea_output(Pc=parameters.chamberPressure, MR=parameters.oxidizerFuelRatio, eps=expansionAreaRatio, short_output=1)  # TODO: use mass not mole?

	print(ceaOutput)

	exhaustComposition = extractExhaustComposition(ceaOutput)
	checkExhaustComposition(exhaustComposition)
	exhaustComposition = convertMoleToMass(exhaustComposition)

	return chamberTemperature, parameters.chamberPressure * 10 ** 5, exhaustComposition
