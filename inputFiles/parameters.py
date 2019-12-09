# ENGINE GENERATOR INPUT FILE

# NOZZLE INPUT DATA (Exhaust gas composition and Chamber Temperature can be calculated with NASA CEA)

# Data input choice ('F' for File, 'M' for Manual)
ceaDataSource = 'F'

# Name of CEA data input file (CEA-Settings: T in Kelvin, P in Bar, Mole Fractions)
ceaDataFileName = 'inputFiles/ceainput.txt'
# Input definition ('mole' for mole fraction, 'mass' for massfraction)
exhaustCompositionRatioType = 'mole'

# Manual Definition of Chamber Temperature
chamberTemperature = 2870.81  # K
# Manual Definition of Chamber Pressure
chamberPressure = 25 * 10 ** 5  # Pa
# Manual definition of exhaust gas composition, Input: Substancename:Massfraction/Molefraction
exhaustComposition = {  'H2O': 2.3579 * 10 ** -1,
						'CO2': 5.5019 * 10 ** -2,
						'CO': 1.7712 * 10 ** -1,
						'Oxygen': 0,
						'Nitrogen': 4.3 * 10 ** -1,
						'Hydrogen': 1.0656 * 10 ** -1,
						'Methane': 0,
						'NH3': 0}

# Fuel
fuelType = "Ethanol"
# Oxidizer
oxidizerType = "N2O"
# Mixture Ratio (O/F Mass)
oxidizerFuelRatio = 3.4

# Ambient Pressure
ambientPressure = 10 ** 5  # Pa
# Optimal expansion altitude ratio (hoptimal/hmax)
overexpansionRatio = 0.333

# Engine Thrust at ambient pressure
seaLevelThrust = 5000  # N
# Burntime
burnDuration = 30  # s
# Combustion Chamber Velocity
chamberVelocity = 40  # m/s
# Ispcorrection (1 for standard, scaling factor in case of reduced isp)
ispCorrectionFactor = 1

# NOZZLE SIMULATION SETUP

# Cell Numbers
nozzleSimCellCount = 50  # Nodimension

# INPUT DATA PROCESSING

# Name of OpenRocket output file
orDataFileName = "inputFiles/pressuredata.csv"
# Data Strip Factor (Rawdatapoints/Outputdatapoints)
orDataStripFactor = 15

# CGDETERMINATION
# Tankdiameter
tankDiameter = 0.20  # m
# Tankstructuremass per unit length for reference diameter
refTankMassPerLength = 2.5  # kg/m
# Referencediameter
referenceTankDiameter = 0.20
# Density Carbon
densityCarbon = 1600  # kg/m^3
# Dead Propellant Mass Fraction
deadFuelMassFraction = 0.05
# Dead Oxidiser Mass Fraction
deadOxidizerMassFraction = 0.05
# Systemarrangement mass (from bottom to top, for fueltank: 'F', for oxidizer: 'O','C' for Coax)
massArrangement = (1, 3.5, 'O', 'F', 3.5)  # kg
# Systemarrangement length (from bottom to top, for fueltank: 'F', for oxidizer: 'O','C' for Coax)
lengthArrangement = (0.41, 0.3, 'O', 'F', 0.3)  # m
# Propellant Storage Conditions
fuelTankTemperature = 25 + 273.15  # K
fuelTankPressure = 30 * 10 ** 5  # Pa
oxidizerTankTemperature = 25 + 273.15  # K
oxidizerTankPressure = 50 * 10 ** 5  # Pa
oxidizerTankGasFraction = 0
# Deadpropellantcondition ('g' for gaseous,'l' for liquid)
deadOxidizerState = 'g'
deadFuelState = 'l'

# OUTPUT DATA PROCESSING

# Output File Name
engineFileName = 'outputFiles/Amalia.rse'
# Rocket Engine Name
engineName = 'Amalia'
# Producer
engineManufacturer = 'TXV'
# Displayed System Diameter
displayedSystemDiameter = 0.1  # m
# Autocalcmass
automaticMassCalculation = 0