from inputFiles import parameters
from CoolProp.CoolProp import PropsSI as ps


# Ideal gas constant
def idealGasConstant():
	rval = 0
	for key in parameters.exhaustComposition:
		rval += parameters.exhaustComposition[key] / ps('molarmass', 'P', 200, 'T', 200, key)
	return 8.344598 * rval


# Specific thermal enthalpy
def specificThermalEnthalpy(T, P):
	ste = 0
	for key in parameters.exhaustComposition:
		ste += parameters.exhaustComposition[key] * ps('H', 'P', P, 'T', T, key)
	return ste


# Specific heats ratio
def specificHeatsRatio(T, P):
	cpval = 0
	cvval = 0
	for key in parameters.exhaustComposition:
		cpval += parameters.exhaustComposition[key] * ps('C', 'P', P, 'T', T, key)
		cvval += parameters.exhaustComposition[key] * ps('CVMASS', 'P', P, 'T', T, key)
	return cpval / cvval
