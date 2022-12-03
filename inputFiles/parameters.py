########################################################################################################################
# Engine Design Input Parameters
########################################################################################################################

# name
name = "Skuld"
# Fuel
fuelType = "Ethanol"
# Water mass fraction in case of fueltype "EthanolWater"
waterFraction = 20.0  # %
# Oxidizer
oxidizerType = "LOX"
# Mixture Ratio (O/F mass flow)
oxidizerFuelRatio = 1.8
# Chamber Pressure
chamberPressure = 40.0 * 1e5  # Pa
# Reference ambient pressure
referenceAmbientPressure = 1.0 * 1e5  # Pa
# Engine thrust at reference ambient pressure
referenceThrust = 2000  # N
# Efficiency factor, scales ISP
engineEfficiency = 0.95

########################################################################################################################
# Simulation Parameters
########################################################################################################################

# Maximum burn duration, engine gets switched off afterwards
maxBurnDuration = 20.0  # s

########################################################################################################################
# Propellant Tank Parameters
########################################################################################################################

# Propellant Storage Conditions
fuelTemperature = 20 + 273.15  # K
fuelTankPressure = 60 * 10**5  # Pa
fuelPressurantTemperature = 25 + 273.15  # K
fuelPressurantTankPressure = 270 * 10**5  # Pa
oxidizerTemperature = -200 + 273.15  # K
oxidizerTankPressure = 60 * 10 ** 5  # Pa
oxidizerPressurantTemperature = 25 + 273.15  # K
oxidizerPressurantTankPressure = 270 * 10**5  # Pa

########################################################################################################################
# Input Data Settings
########################################################################################################################

# Name of OpenRocket output file
orDataFileName = "inputFiles/pressuredata2.csv"
# Data subsampling factor
orDataReductionFactor = 1


########################################################################################################################
# Output Data Settings TODO: use in ORLEG.py only
########################################################################################################################

# Output File Name
engineFileName = 'outputFiles/Skuld.rse'
# Rocket Engine Name
engineName = 'Skuld'
# Producer
engineManufacturer = 'TUST'
# Displayed System Diameter
displayedSystemDiameter = 0.06  # m
# Automatic Mass Calculation
automaticMassCalculation = 0
