from cea import getCeaData
from inputFiles import parameters
import thermodynamics as thermo
import numpy

chamberTemperature = None
chamberPressure = None
exhaustComposition = None


# Isentropic Flow Equation (Kappa Upwind), returns T2
def calculateTemperatureIsentropicFlow(T1, p2, p1):
	return T1 * (p2 / p1) ** ((thermo.specificHeatsRatio(T1, p1, exhaustComposition) - 1) / (thermo.specificHeatsRatio(T1, p1, exhaustComposition)))


# Conservation of energy, returns v2
def calculateVelocityConservationOfEnergy(T1, v1, p1, T2, p2):
	return numpy.sqrt(2 * ((0.5 * v1 ** 2) + thermo.specificThermalEnthalpy(T1, p1, exhaustComposition) - thermo.specificThermalEnthalpy(T2, p2, exhaustComposition)))


# Density
def calculateDensity(p2, T2):
	return p2 / (thermo.idealGasConstant(exhaustComposition) * T2)


# Diameter
def calculateExitArea(T2, p2, v2, rho2, massFlowRate):
	return massFlowRate / (rho2 * v2)


def simulateEngine(refAmbientPressure):
	global chamberTemperature, chamberPressure, exhaustComposition
	chamberTemperature, chamberPressure, exhaustComposition = getCeaData()

	# Definition of pressure step size
	pressureStep = (chamberPressure - refAmbientPressure) / parameters.nozzleSimCellCount
	# Definition of initial conditions (temperature, pressure, velocity)
	T1 = T2 = chamberTemperature
	p1 = p2 = chamberPressure
	v1 = v2 = parameters.chamberVelocity
	# Expand down to ambient pressure
	while p1 > 1.01 * refAmbientPressure:
		p2 = p1 - pressureStep
		T2 = calculateTemperatureIsentropicFlow(T1, p2, p1)
		v2 = calculateVelocityConservationOfEnergy(T1, v1, p1, T2, p2)
		T1 = T2
		p1 = p2
		v1 = v2
	# Calculate with values after expansion
	v2 = v2 * parameters.ispCorrectionFactor
	specificImpulse = v2 / 9.81
	density = calculateDensity(p2, T2)
	massFlowRate = parameters.seaLevelThrust / (v2 + (p2 - parameters.ambientPressure) / (
				density * v2))  # mass flow calculated for input thrust at ground level (overexpanding engine)
	exitArea = calculateExitArea(T2, p2, v2, density, massFlowRate)
	refThrust = massFlowRate * v2
	print("Engine Simulation done, massFLowRate: " + str(massFlowRate) + " specificImpulse: " + str(
		specificImpulse) + " refThrust: " + str(refThrust))
	return massFlowRate, specificImpulse, exitArea, refThrust


# calculation of engine thrust curve due to altitude compensation (According to Huzel/Huang Page 2)
def calcThrustAltComp(refAmbientPressure, ambientPressureList, optimalThrust, exitArea):
	thrustList = []
	for ambientPressure in ambientPressureList:
		val = optimalThrust + exitArea * (refAmbientPressure - ambientPressure)
		thrustList.append(val)
	maximumThrust = thrustList[-1]
	averageThrust = (thrustList[0] + thrustList[-1]) / 2
	print("Engine Altitude Compensation done, averageThrust: " + str(averageThrust) + " maximumThrust: " + str(
		maximumThrust))
	return thrustList, averageThrust, maximumThrust
