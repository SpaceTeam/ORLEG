from typing import List

from param_types import (
    VolumeCubicMeter,
    LengthMeter,
    MassKiloGramm,
    CoolPropFluid,
    TKelvin,
    PPascal,
    DensityKGPCM,
)

from CoolProp.CoolProp import PropsSI


class MassObject(object):
    def __init__(
        self, mass: MassKiloGramm, length: LengthMeter, cg: LengthMeter = None
    ):
        """Object with mass.

        :param cg: center of gravity from bottom of object
        """
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
    def calculateTotalMass(massObjectList: List["MassObject"]):
        totalMass = 0
        for massObject in massObjectList:
            totalMass += massObject.getMass()
        return totalMass

    @staticmethod
    def calculateTotalStructuralMass(massObjectList: List["MassObject"]):
        totalMass = 0
        for massObject in massObjectList:
            try:
                mass = massObject.getTankMass()
            except AttributeError:
                mass = massObject.getMass()
            totalMass += mass
        return totalMass

    @staticmethod
    def calculateTotalDryMass(massObjectList: List["MassObject"]):
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
    def calculateTotalLength(massObjectList: List["MassObject"]):
        totalLength = 0
        for massObject in massObjectList:
            totalLength += massObject.getLength()
        return totalLength

    @staticmethod
    def calculateTotalCG(massObjectList: List["MassObject"]):
        sum = 0
        length = 0
        for massObject in massObjectList:
            sum += (length + massObject.getCG()) * massObject.getMass()
            length += massObject.getLength()
        return sum / MassObject.calculateTotalMass(massObjectList)


class GasLiquidTank(MassObject):
    """Class to represent a tank that has a liquid stored
    together with a gas (pressurant).
    """

    def __init__(
        self,
        tankVolume: VolumeCubicMeter,
        tankLength: LengthMeter,
        tankMass: MassKiloGramm,
        liquidType: CoolPropFluid,
        liquidTemperature: TKelvin,
        gasType: CoolPropFluid,
        gasTemperature: TKelvin,
        fillLevel: float,
        tankPressure: PPascal,
        tankCG: LengthMeter = None,
    ):
        # static values
        self.tankVolume = tankVolume
        self.tankLength = tankLength
        self.tankMass = tankMass
        self.liquidType = liquidType
        self.tankCG = tankCG or tankLength / 2

        # assumed static values
        self.liquidTemperature = liquidTemperature
        self.gasType = gasType
        self.gasTemperature = gasTemperature
        self.liquidDensity = PropsSI(
            "D", "P", tankPressure, "T", self.liquidTemperature, self.liquidType.value
        )

        # dynamic values
        self.liquidMass = self.tankVolume * fillLevel * self.liquidDensity
        self.gasMass = (
            self.tankVolume
            * (1 - fillLevel)
            * PropsSI(
                "D", "P", tankPressure, "T", self.gasTemperature, self.gasType.value
            )
        )

    def getTankMass(self):
        return self.tankMass

    def getLiquidMass(self):
        return self.liquidMass

    def getGasMass(self):
        return self.gasMass

    def getMass(self):
        """Sum of tank and fluid masses"""
        return self.tankMass + self.liquidMass + self.gasMass

    def getCG(self) -> LengthMeter:
        """Calculate center of gravity for tank in combination with
        gas and liquid.

        :return: Distance of cg from bottom of tank.
        """
        liquid_fraction = self.getLiquidVolume() / self.tankVolume
        gas_fraction = self.getGasVolume() / self.tankVolume
        liquidCG = 0.5 * liquid_fraction * self.tankLength
        gasCG = self.tankLength - 0.5 * gas_fraction * self.tankLength
        return (
            self.tankCG * self.tankMass
            + liquidCG * self.liquidMass
            + gasCG * self.gasMass
        ) / self.getMass()

    def getLength(self) -> LengthMeter:
        return self.tankLength

    def getLiquidVolume(self) -> VolumeCubicMeter:
        return self.liquidMass / self.liquidDensity

    def getGasVolume(self) -> VolumeCubicMeter:
        return self.tankVolume - self.getLiquidVolume()

    def getGasDensity(self) -> DensityKGPCM:
        return self.gasMass / self.getGasVolume()

    def getTankPressure(self) -> PPascal:
        """Get pressure of gas with current density and volume."""
        return PropsSI(
            "P", "D", self.getGasDensity(), "T", self.gasTemperature, self.gasType.value
        )

    def removeLiquidMass(
        self, removedLiquidMass: MassKiloGramm
    ) -> MassKiloGramm:  # FIXME: isotherm, not realistic
        """Substract the given mass of the liquid mass
        Will only remove what's left if trying to remove
        more than what is left over.

        :return: The removed liquid mass
        """
        if removedLiquidMass >= self.liquidMass:
            removedLiquidMass = self.liquidMass
        self.liquidMass -= removedLiquidMass
        return removedLiquidMass

    def removeLiquidMassKeepTankPressure(self, removedLiquidMass: MassKiloGramm):
        """Remove liquid mass and recalculate the gass mass
        with the new gas volume.
        """
        oldTankPressure = self.getTankPressure()
        removedLiquidMass = self.removeLiquidMass(removedLiquidMass)
        addedGasMass = self.setTankPressure(oldTankPressure)
        return removedLiquidMass, addedGasMass

    def addGasMass(self, addedGasMass: MassKiloGramm):  # FIXME: isotherm, not realistic
        """Add the mass to self.gasMass"""
        self.gasMass += addedGasMass

    def setTankPressure(
        self, tankPressure: PPascal
    ) -> MassKiloGramm:  # FIXME: isotherm, not realistic
        """Recalculate the gas mass with the given tank pressure
        and set self.gasMass to the result.

        :return: difference in gas mass       
        """
        oldGasMass = self.gasMass
        gasDensity = PropsSI(
            "D", "P", tankPressure, "T", self.gasTemperature, self.gasType.value
        )
        self.gasMass = self.getGasVolume() * gasDensity
        return self.gasMass - oldGasMass


class GasTank(GasLiquidTank):
    """Childclass of GasLiquidTank that defaults
    the fill level to 0 to represent a tank filled only
    with gas.
    """
    def __init__(
        self,
        tankVolume: VolumeCubicMeter,
        tankLength: LengthMeter,
        tankMass: MassKiloGramm,
        gasType: CoolPropFluid,
        gasTemperature: TKelvin,
        tankPressure: PPascal,
    ):
        super().__init__(
            tankVolume=tankVolume,
            tankLength=tankLength,
            tankMass=tankMass,
            liquidType=CoolPropFluid("Water"),
            liquidTemperature=300,
            gasType=gasType,
            gasTemperature=gasTemperature,
            fillLevel=0,
            tankPressure=tankPressure,
        )
