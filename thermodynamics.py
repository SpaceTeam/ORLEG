from CoolProp.CoolProp import PropsSI as ps


# Ideal gas constant
def idealGasConstant(composition):
	rval = 0
	for key in composition:
		rval += composition[key] / ps('molarmass', 'P', 200, 'T', 200, key)
	return 8.344598 * rval


# Specific thermal enthalpy
def specificThermalEnthalpy(T, P, composition):
	ste = 0
	for key in composition:
		ste += composition[key] * ps('H', 'P', P, 'T', T, key)
	return ste


# Specific heats ratio
def specificHeatsRatio(T, P, composition):
	cpval = 0
	cvval = 0
	for key in composition:
		cpval += composition[key] * ps('C', 'P', P, 'T', T, key)
		cvval += composition[key] * ps('CVMASS', 'P', P, 'T', T, key)
	return cpval / cvval
