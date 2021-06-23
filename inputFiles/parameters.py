########################################################################################################################
# Engine Design Input Parameters
########################################################################################################################

# name
name = "Amalia"
# Fuel
fuelType = "Ethanol"
# Water mass fraction in case of fueltype "EthanolWater"
waterFraction = 30.0  # %
# Oxidizer
oxidizerType = "LOX"
# Mixture Ratio (O/F mass flow)
oxidizerFuelRatio = 1.5
# Chamber Pressure
chamberPressure = 10.0 * 10**5  # Pa
# Reference ambient pressure
referenceAmbientPressure = 1.0 * 10**5  # Pa
# Engine thrust at reference ambient pressure
referenceThrust = 700  # N
# Efficiency factor, scales ISP
engineEfficiency = 0.80

########################################################################################################################
# Simulation Parameters
########################################################################################################################

# Maximum burn duration, engine gets switched off afterwards
maxBurnDuration = 20  # s

########################################################################################################################
# Propellant Tank Parameters
########################################################################################################################

# Propellant Storage Conditions
fuelTemperature = 20 + 273.15  # K
fuelTankPressure = 30 * 10**5  # Pa
fuelPressurantTemperature = 25 + 273.15  # K
fuelPressurantTankPressure = 270 * 10**5  # Pa
oxidizerTemperature = -200 + 273.15  # K
oxidizerTankPressure = 30 * 10 ** 5  # Pa
oxidizerPressurantTemperature = 25 + 273.15  # K
oxidizerPressurantTankPressure = 270 * 10**5  # Pa

########################################################################################################################
# Input Data Settings
########################################################################################################################

# Name of OpenRocket output file
orDataFileName = "inputFiles/pressuredata.csv"
# Data subsampling factor
orDataReductionFactor = 1


########################################################################################################################
# Output Data Settings TODO: use in ORLEG.py only
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
