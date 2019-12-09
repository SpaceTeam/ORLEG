from inputFiles import parameters
from CoolProp.CoolProp import PropsSI as ps


# Ideal Gas Constant
def Rgas():
	rval = 0
	for key in parameters.sw:
		rval += parameters.sw[key] / ps('molarmass', 'P', 200, 'T', 200, key)
	R = 8.344598 * rval
	return R


# Specific thermal enthalpy
def hgas(T, P):
	hval = 0
	for key in parameters.sw:
		hval += parameters.sw[key] * ps('H', 'P', P, 'T', T, key)
	return hval


# Specific heats ratio
def kgas(T, P):
	cpval = 0
	cvval = 0
	for key in parameters.sw:
		cpval += parameters.sw[key] * ps('C', 'P', P, 'T', T, key)
		cvval += parameters.sw[key] * ps('CVMASS', 'P', P, 'T', T, key)
	kappa = cpval / cvval
	return kappa
