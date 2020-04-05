########################################################################################################################
# Engine Parameters
########################################################################################################################

# name
name = "Amalia"
# Fuel
fuelType = "Ethanol"
# Water mass fraction in case of fueltype "EthanolWater"
waterFraction = 30.0  # %
# Oxidizer
oxidizerType = "N2O"
# Mixture Ratio (O/F mass flow)
oxidizerFuelRatio = 3.0
# Chamber Pressure
chamberPressure = 10.0 * 10**5  # Pa
# Reference ambient pressure
referenceAmbientPressure = 1.0 * 10**5  # Pa
# Engine thrust at reference ambient pressure
referenceThrust = 500  # N
# Efficiency factor, scales ISP
engineEfficiency = 0.95

########################################################################################################################
# Tank Parameters
########################################################################################################################

# Burntime
burnDuration = 8  # s

# Tank Diameter
tankDiameter = 0.09  # m

# Tank (and other stuff) Mass Arrangement (from bottom to top, for fueltank: 'F', for oxidizer: 'O','C' for Coax, mass in kg for other)
#massArrangement = (1.7, 'O', 1.0, 'F', 0.53)  # kg
# Tank (and other stuff) Length Arrangement (from bottom to top, for fueltank: 'F', for oxidizer: 'O','C' for Coax, length in m for other)
#lengthArrangement = (0.14, 'O', 0.45, 'F', 0.3)  # m

# Tank type ('c' for carbon, 'a' for aluminium)
tankType = 'a'

# Reference Carbon Tank Diameter
referenceCarbonTankDiameter = 0.20  # m
# Reference Carbon Tank mass per length
referenceCarbonTankMassPerLength = 2.5  # kg/m
# Density Carbon
carbonDensity = 1600  # kg/m^3

# Aluminium Tank Endcap Mass
aluminiumTankEndcapMass = 0.25  # kg
# Aluminium Yield Strength
aluminiumYieldStrength = 280 * 10 ** 6  # Pa
# Density Aluminium
aluminiumDensity = 2810  # kg/m^3
# Aluminium Tank Safety Factor
aluminiumTankSafetyFactor = 2
# Aluminium Tank minimum wall thickness
aluminiumTankMinWallThickness = 0.002

# Dead Fuel Mass Fraction
deadFuelMassFraction = 0.05
# Dead Oxidiser Mass Fraction
deadOxidizerMassFraction = 0.05
# Dead Propellant Conditions ('g' for gaseous,'l' for liquid)
deadOxidizerState = 'g'
deadFuelState = 'l'

# Propellant Storage Conditions
fuelTankTemperature = 25 + 273.15  # K
fuelTankPressure = 30 * 10 ** 5  # Pa
oxidizerTankTemperature = 10 + 273.15  # K
oxidizerTankPressure = 45 * 10 ** 5  # Pa
oxidizerTankGasFraction = 0


########################################################################################################################
# Input Data Settings
########################################################################################################################

# Name of OpenRocket output file
orDataFileName = "inputFiles/pressuredata.csv"
# Data subsampling factor
orDataReductionFactor = 1


########################################################################################################################
# Output Data Settings
########################################################################################################################

# Output File Name
engineFileName = 'outputFiles/Amalia_8s.rse'
# Rocket Engine Name
engineName = 'Amalia 8s'
# Producer
engineManufacturer = 'TXV'
# Displayed System Diameter
displayedSystemDiameter = 0.12  # m
# Automatic Mass Calculation
automaticMassCalculation = 0
