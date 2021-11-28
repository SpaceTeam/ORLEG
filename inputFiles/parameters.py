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
oxidizerType = "N2O"
# Mixture Ratio (O/F mass flow)
oxidizerFuelRatio = 3.0
# Chamber Pressure
chamberPressure = 11.0 * 1e5  # Pa
# Reference ambient pressure
referenceAmbientPressure = 1.0 * 1e5  # Pa
# Engine thrust at reference ambient pressure
referenceThrust = 500  # N
# Efficiency factor, scales ISP
engineEfficiency = 0.8

########################################################################################################################
# Simulation Parameters
########################################################################################################################

# Maximum burn duration, engine gets switched off afterwards
maxBurnDuration = 10  # s

########################################################################################################################
# Propellant Tank Parameters
########################################################################################################################

# Propellant Storage Conditions
fuelTemperature = 15 + 273.15  # K
fuelTankPressure = 30 * 1e5  # Pa
fuelPressurantTemperature = 20 + 273.15  # K
fuelPressurantTankPressure = 270 * 1e5  # Pa
oxidizerTemperature = 3 + 273.15  # K
oxidizerTankPressure = 40 * 1e5  # Pa
oxidizerPressurantTemperature = 20 + 273.15  # K
oxidizerPressurantTankPressure = 270 * 1e5  # Pa

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
displayedSystemDiameter = 0.06  # m
# Automatic Mass Calculation
automaticMassCalculation = 0
