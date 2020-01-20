from rocketcea.cea_obj_w_units import CEA_Obj

g0 = 9.81


class Engine(object):

	def __init__(self, name, fuelType, oxidizerType, oxidizerFuelRatio, chamberPressure, referenceAmbientPressure, referenceThrust, engineEfficiency):
		self.name = name
		self.fuelType = fuelType
		self.oxidizerType = oxidizerType
		self.oxidizerFuelRatio = oxidizerFuelRatio
		self.chamberPressure = chamberPressure
		self.referenceAmbientPressure = referenceAmbientPressure
		self.referenceThrust = referenceThrust
		self.engineEfficiency = engineEfficiency

		self.cea = CEA_Obj(oxName=self.oxidizerType, fuelName=self.fuelType, useFastLookup=0, makeOutput=0,
			isp_units='m/sec', cstar_units='m/sec', pressure_units='Bar', temperature_units='K',
			sonic_velocity_units='m/sec', enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K')

		self.areaRatio = self.cea.get_eps_at_PcOvPe(Pc=self.chamberPressure, MR=self.oxidizerFuelRatio, PcOvPe=(self.chamberPressure / self.referenceAmbientPressure))

		(self.exhaustVelocity, expansionMode) = self.cea.estimate_Ambient_Isp(self.chamberPressure, self.oxidizerFuelRatio, self.areaRatio, self.referenceAmbientPressure)

		self.referenceIsp = self.exhaustVelocity / g0

		self.massFlowRate = self.referenceThrust / self.exhaustVelocity

	def printParameters(self):
		print("")
		print("Engine Input Parameters:")
		print("    Name: " + self.name)
		print("    fuelType: " + self.fuelType)
		print("    oxidizerType: " + self.oxidizerType)
		print("    oxidizerFuelRatio: " + str(self.oxidizerFuelRatio))
		print("    chamberPressure: " + str(self.chamberPressure))
		print("    referenceAmbientPressure: " + str(self.referenceAmbientPressure))
		print("    referenceThrust: " + str(self.referenceThrust))
		print("    engineEfficiency: " + str(self.engineEfficiency))
		print("Engine Output Parameters:")
		print("    areaRatio: " + str(self.areaRatio))
		print("    referenceIsp: " + str(self.referenceIsp))
		print("    massFlow: " + str(self.massFlowRate))

	def isp(self, ambientPressure=None, oxidizerFuelRatio=None, chamberPressure=None):
		if ambientPressure is None:
			ambientPressure = self.referenceAmbientPressure
		if oxidizerFuelRatio is None:
			oxidizerFuelRatio = self.oxidizerFuelRatio
		if chamberPressure is None:
			chamberPressure = self.chamberPressure

		(isp, expansionMode) = self.cea.estimate_Ambient_Isp(chamberPressure, oxidizerFuelRatio, self.areaRatio, ambientPressure)
		return isp / g0

	def thrust(self, ambientPressure=None, massFlowRate=None, oxidizerFuelRatio=None, chamberPressure=None):
		if massFlowRate is None:
			massFlowRate = self.massFlowRate

		return massFlowRate * self.isp(ambientPressure, oxidizerFuelRatio, chamberPressure) * g0
