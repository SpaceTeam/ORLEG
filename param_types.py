from enum import Enum


class VolumeCubicMeter(float):
    """A volume in cubic meters"""

    pass


class LengthMeter(float):
    """A length in meters"""

    pass


class MassKiloGramm(float):
    """A mass in kilogramms"""

    pass


class CoolPropFluid(Enum):
    """Fluid string of coolprop library

    Couldn't find full documentation yet.
    See: http://www.coolprop.org/coolprop/HighLevelAPI.html
    """

    Nitrogen = "Nitrogen"
    Ethanol = "Ethanol"
    N2O = "N2O"
    Water = "Water"
    LOX = "LOX"


class CEAFuelType(Enum):
    """One of RocketCEA supported fuel types
    see https://rocketcea.readthedocs.io/en/latest/propellants.html
    """

    Ethanol = "Ethanol"


class CEAOxidizerType(Enum):
    """One of RocketCEA supported oxidizer types
    see https://rocketcea.readthedocs.io/en/latest/propellants.html
    """

    N2O = "N2O"
    LOX = "LOX"


class TKelvin(float):
    """Temperature value in Kelvin."""


class PPascal(float):
    """Pressure in Pascal."""


class DensityKGPCM(float):
    """Density in kg/m³"""


class FNewton(float):
    """Force in Newton"""


class CustomFuels(Enum):
    ETHANOL_WATER = "EthanolWater"
