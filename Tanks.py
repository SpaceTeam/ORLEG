from CoolProp.CoolProp import PropsSI


class MassObject(object):
	def __init__(self, mass, length, cg=None):
		self.mass = mass
		self.length = length
		if cg is None:
			self.cg = self.length / 2
		else:
			self.cg = cg

	def getMass(self):
		return self.mass

	def getCG(self):
		return self.cg

	def getLength(self):
		return self.length

	@staticmethod
	def calculateTotalMass(massObjectList):
		totalMass = 0
		for massObject in massObjectList:
			totalMass += massObject.getMass()
		return totalMass

	@staticmethod
	def calculateTotalStructuralMass(massObjectList):
		totalMass = 0
		for massObject in massObjectList:
			try:
				mass = massObject.getTankMass()
			except AttributeError:
				mass = massObject.getMass()
			totalMass += mass
		return totalMass

	@staticmethod
	def calculateTotalDryMass(massObjectList):
		totalMass = 0
		for massObject in massObjectList:
			try:
				mass = massObject.getGasMass()
			except AttributeError:
				mass = 0
			totalMass += mass
		totalMass += MassObject.calculateTotalStructuralMass(massObjectList)
		return totalMass

	@staticmethod
	def calculateTotalLength(massObjectList):
		totalLength = 0
		for massObject in massObjectList:
			totalLength += massObject.getLength()
		return totalLength

	@staticmethod
	def calculateTotalCG(massObjectList):
		sum = 0
		length = 0
		for massObject in massObjectList:
			sum += (length + massObject.getCG()) * massObject.getMass()
			length += massObject.getLength()
		return sum / MassObject.calculateTotalMass(massObjectList)


class GasLiquidTank(MassObject):
	def __init__(self, tankVolume, tankLength, tankMass, liquidType, liquidTemperature, gasType, gasTemperature, fillLevel, tankPressure):
		# static values
		self.tankVolume = tankVolume
		self.tankLength = tankLength
		self.tankMass = tankMass
		self.liquidType = liquidType

		# assumed static values
		self.liquidTemperature = liquidTemperature
		self.gasType = gasType
		self.gasTemperature = gasTemperature
		self.liquidDensity = PropsSI('D', 'P', tankPressure, 'T', self.liquidTemperature, self.liquidType)

		# dynamic values
		self.liquidMass = self.tankVolume * fillLevel * self.liquidDensity
		self.gasMass = self.tankVolume * (1 - fillLevel) * PropsSI('D', 'P', tankPressure, 'T', self.gasTemperature, self.gasType)

	def getTankMass(self):
		return self.tankMass

	def getLiquidMass(self):
		return self.liquidMass

	def getGasMass(self):
		return self.gasMass

	def getMass(self):
		return self.tankMass + self.liquidMass + self.gasMass

	def getCG(self):
		tankCG = self.tankLength / 2
		liquidCG = self.getLiquidVolume() / self.tankVolume * tankCG
		gasCG = self.tankLength - (self.getGasVolume() / self.tankVolume * tankCG)
		return (tankCG * self.tankMass + liquidCG * self.liquidMass + gasCG * self.gasMass) / self.getMass()

	def getLength(self):
		return self.tankLength

	def getLiquidVolume(self):
		return self.liquidMass / self.liquidDensity

	def getGasVolume(self):
		return self.tankVolume - self.getLiquidVolume()

	def getGasDensity(self):
		gasVolume = self.tankVolume - self.getLiquidVolume()
		return self.gasMass / gasVolume

	def getTankPressure(self):
		gasDensity = self.gasMass / self.getGasVolume()
		return PropsSI('P', 'D', gasDensity, 'T', self.gasTemperature, self.gasType)

	def removeLiquidMass(self, removedLiquidMass):  # FIXME: isotherm, not realistic
		if removedLiquidMass >= self.liquidMass:
			removedLiquidMass = self.liquidMass
		self.liquidMass -= removedLiquidMass
		return removedLiquidMass

	def removeLiquidMassKeepTankPressure(self, removedLiquidMass):
		oldTankPressure = self.getTankPressure()
		removedLiquidMass = self.removeLiquidMass(removedLiquidMass)
		addedGasMass = self.setTankPressure(oldTankPressure)
		return removedLiquidMass, addedGasMass

	def addGasMass(self, addedGasMass):  # FIXME: isotherm, not realistic
		self.gasMass += addedGasMass

	def setTankPressure(self, tankPressure):  # FIXME: isotherm, not realistic
		oldGasMass = self.gasMass
		self.gasMass = self.getGasVolume() * PropsSI('D', 'P', tankPressure, 'T', self.gasTemperature, self.gasType)
		return self.gasMass - oldGasMass


class GasTank(GasLiquidTank):
	def __init__(self, tankVolume, tankLength, tankMass, gasType, gasTemperature, tankPressure):
		super().__init__(tankVolume=tankVolume, tankLength=tankLength, tankMass=tankMass, liquidType='Water', liquidTemperature=300, gasType=gasType, gasTemperature=gasTemperature, fillLevel=0, tankPressure=tankPressure)
