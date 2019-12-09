from inputFiles import parameters
import ceaDataReader
from CoolProp.CoolProp import PropsSI


# Check if the sum of the exhaust gas fraction is close enough to 1
def checkExhaustComposition():
	fractionSum = 0
	for key in parameters.exhaustComposition:
		fractionSum += parameters.exhaustComposition[key]
	if abs(fractionSum - 1) > 0.008:
		print('WARNING! exhaust fraction sum out of boundaries:', fractionSum)


# If required, convert exhaust composition from mole to mass fractions
def convertMoleToMass():
	if parameters.exhaustCompositionRatioType == 'mass':
		pass
	elif parameters.exhaustCompositionRatioType == 'mole':
		molarMassSum = 0
		for key in parameters.exhaustComposition:
			molarMassSum += parameters.exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key)
		for key in parameters.exhaustComposition:
			parameters.exhaustComposition[key] = parameters.exhaustComposition[key] * PropsSI('molarmass', 'P', 200, 'T', 200, key) / molarMassSum
	else:
		print('ERROR! Invalid setting for parameter exhaustCompositionRatioType')


# Process input data, calls functions above
def processInputData():
	if parameters.ceaDataSource == 'F':
		parameters.chamberTemperature, parameters.exhaustComposition, parameters.chamberPressure = ceaDataReader.readCea(parameters.ceaDataFileName)
	elif parameters.ceaDataSource == 'M':
		pass
	else:
		print('ERROR! Invalid setting for parameter ceaDataSource')

	checkExhaustComposition()
	convertMoleToMass()
