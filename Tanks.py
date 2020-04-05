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
	def calculateTotalCG(massObjectList):
		sum = 0
		length = 0
		for massObject in massObjectList:
			sum += (length + massObject.getCG()) * massObject.getMass()
			length += massObject.getLength()
		return sum / MassObject.calculateTotalMass(massObjectList)


class Tank(MassObject):
	def __init__(self, tankVolume, tankLength, tankMass, fluidType, fluidTemperature, pressurantType, pressurantTemperature, fillLevel, tankPressure):
		# static values
		self.tankVolume = tankVolume
		self.tankLength = tankLength
		self.tankMass = tankMass
		self.fluidType = fluidType

		# assumed static values
		self.fluidTemperature = fluidTemperature
		self.pressurantType = pressurantType
		self.pressurantTemperature = pressurantTemperature
		self.fluidDensity = PropsSI('D', 'P', tankPressure, 'T', self.fluidTemperature, self.fluidType)

		# dynamic values
		self.fluidMass = self.tankVolume * fillLevel * self.fluidDensity
		self.pressurantMass = self.tankVolume * (1 - fillLevel) * PropsSI('D', 'P', tankPressure, 'T', self.pressurantTemperature, self.pressurantType)

	def getTankMass(self):
		return self.tankMass

	def getFluidMass(self):
		return self.fluidMass

	def getPressurantMass(self):
		return self.pressurantMass

	def getMass(self):
		return self.tankMass + self.fluidMass + self.pressurantMass

	def getCG(self):
		tankCG = self.tankLength / 2
		fluidCG = self.getFluidVolume() / self.tankVolume * tankCG
		pressurantCG = self.tankLength - (self.getPressurantVolume() / self.tankVolume * tankCG)
		return (tankCG * self.tankMass + fluidCG * self.fluidMass + pressurantCG * self.pressurantMass) / self.getMass()

	def getLength(self):
		return self.tankLength

	def getFluidVolume(self):
		return self.fluidMass / self.fluidDensity

	def getPressurantVolume(self):
		return self.tankVolume - self.getFluidVolume()

	def getPressurantDensity(self):
		pressurantVolume = self.tankVolume - self.getFluidVolume()
		return self.pressurantMass / pressurantVolume

	def getTankPressure(self):
		pressurantDensity = self.pressurantMass - self.getPressurantVolume()
		return PropsSI('P', 'D', pressurantDensity, 'T', self.pressurantTemperature, self.pressurantType)

	def removeFluidMass(self, removedFluidMass):  # FIXME: isotherm, not realistic
		if removedFluidMass >= self.fluidMass:
			removedFluidMass = self.fluidMass
		self.fluidMass -= removedFluidMass
		return removedFluidMass

	def removeFluidMassKeepTankPressure(self, removedFluidMass):
		oldTankPressure = self.getTankPressure()
		removedFluidMass = self.removeFluidMass(removedFluidMass)
		addedPressurantMass = self.setTankPressure(oldTankPressure)
		return removedFluidMass, addedPressurantMass

	def addPressurantMass(self, addedPressurantMass):  # FIXME: isotherm, not realistic
		self.pressurantMass += addedPressurantMass

	def setTankPressure(self, tankPressure):  # FIXME: isotherm, not realistic
		oldPressurantMass = self.pressurantMass
		self.pressurantMass = self.getPressurantVolume() * PropsSI('D', 'P', tankPressure, 'T', self.fluidTemperature, self.fluidType)
		return self.pressurantMass - oldPressurantMass
