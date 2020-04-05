from rocketcea.cea_obj_w_units import CEA_Obj
from rocketcea.cea_obj import add_new_fuel

g0 = 9.81


class Engine(object):

	def __init__(self, name, fuelType, oxidizerType, oxidizerFuelRatio, chamberPressure, referenceAmbientPressure, referenceThrust, engineEfficiency, waterFraction=0.0):
		self.name = name
		self.fuelType = fuelType
		self.oxidizerType = oxidizerType
		self.oxidizerFuelRatio = oxidizerFuelRatio
		self.chamberPressure = chamberPressure
		self.referenceAmbientPressure = referenceAmbientPressure
		self.referenceThrust = referenceThrust
		self.engineEfficiency = engineEfficiency

		if fuelType == "EthanolWater":
			card_str = """
			fuel C2H5OH(L)   C 2 H 6 O 1   wt%=""" + str(100.0 - waterFraction) + """
			h,cal=-66370.0     t(k)=298.15
			fuel water   H 2 O 1   wt%=""" + str(waterFraction) + """
			h,cal=-68308.0     t(k)=298.15     rho,g/cc = 0.9998
			"""
			add_new_fuel('EthanolWater', card_str)

		self.cea = CEA_Obj(oxName=self.oxidizerType, fuelName=self.fuelType, useFastLookup=0, makeOutput=0,
			isp_units='m/sec', cstar_units='m/sec', pressure_units='Pa', temperature_units='K',
			sonic_velocity_units='m/sec', enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K')

		self.areaRatio = self.cea.get_eps_at_PcOvPe(Pc=self.chamberPressure, MR=self.oxidizerFuelRatio, PcOvPe=(self.chamberPressure / self.referenceAmbientPressure))

		self.exhaustVelocity = self.getExhaustVelocity()

		self.referenceIsp = self.exhaustVelocity / g0

		self.massFlowRate = self.referenceThrust / self.exhaustVelocity

		self.fuelMassFlowRate = self.massFlowRate / (self.oxidizerFuelRatio + 1)

		self.oxMassFlowRate = self.massFlowRate / (self.oxidizerFuelRatio + 1) * self.oxidizerFuelRatio

		self.combustionTemperature = self.cea.get_Tcomb(self.chamberPressure, self.oxidizerFuelRatio)

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
		print("    combustionTemperature: " + str(self.combustionTemperature))

	def getExhaustVelocity(self, ambientPressure=None, oxidizerFuelRatio=None, chamberPressure=None):
		if ambientPressure is None:
			ambientPressure = self.referenceAmbientPressure
		if oxidizerFuelRatio is None:
			oxidizerFuelRatio = self.oxidizerFuelRatio
		if chamberPressure is None:
			chamberPressure = self.chamberPressure

		(ve, expansionMode) = self.cea.estimate_Ambient_Isp(chamberPressure, oxidizerFuelRatio, self.areaRatio, ambientPressure)
		if expansionMode == 'Separated':
			print("WARNING: Flow separation in nozzle!")

		ve *= self.engineEfficiency

		return ve

	def getThrust(self, ambientPressure=None, massFlowRate=None, oxidizerFuelRatio=None, chamberPressure=None):
		if massFlowRate is None:
			massFlowRate = self.massFlowRate

		return massFlowRate * self.getExhaustVelocity(ambientPressure, oxidizerFuelRatio, chamberPressure)
