#!/usr/bin/env python3
from inputFiles import parameters
from Engine import Engine
import orSimDataReader
from Tanks import MassObject, GasLiquidTank, GasTank
import orEngineFileWriter


engine = Engine(
    parameters.name,
    parameters.fuelType,
    parameters.fuelTemperature,
    parameters.oxidizerType,
    parameters.oxidizerTemperature,
    parameters.oxidizerFuelRatio,
    parameters.chamberPressure,
    parameters.referenceAmbientPressure,
    parameters.referenceThrust,
    parameters.engineEfficiency,
    parameters.waterFraction,
)

engineBay = MassObject(mass=1.680, length=0.294, cg=0.150)
oxTank = GasLiquidTank(
    tankVolume=2400e-6,
    tankLength=0.387,
    tankMass=1.170,
    liquidType=parameters.oxidizerType,
    liquidTemperature=parameters.oxidizerTemperature,
    gasType="Nitrogen",
    gasTemperature=240,
    fillLevel=0.95,
    tankPressure=parameters.oxidizerTankPressure,
)  # Aluminium
# oxTank = GasLiquidTank(tankVolume=2400e-6, tankLength=0.387, tankMass=1.925, liquidType=parameters.oxidizerType, liquidTemperature=parameters.oxidizerTemperature, gasType='Nitrogen', gasTemperature=240, fillLevel=0.95, tankPressure=parameters.oxidizerTankPressure)  # Steel
oxPress = MassObject(mass=0.55, length=0.095)
oxPressTank = GasTank(
    tankVolume=800e-6,
    tankLength=0.196,
    tankMass=0.7,
    gasTemperature=parameters.oxidizerPressurantTemperature,
    gasType="Nitrogen",
    tankPressure=parameters.oxidizerPressurantTankPressure,
)
fuelTank = GasLiquidTank(
    tankVolume=900e-6,
    tankLength=0.192,
    tankMass=0.594,
    liquidType=parameters.fuelType,
    liquidTemperature=parameters.fuelTemperature,
    gasType="Nitrogen",
    gasTemperature=250,
    fillLevel=0.99,
    tankPressure=parameters.fuelTankPressure,
)  # Aluminium
# fuelTank = GasLiquidTank(tankVolume=900e-6, tankLength=0.192, tankMass=0.876, liquidType=parameters.fuelType, liquidTemperature=parameters.fuelTemperature, gasType='Nitrogen', gasTemperature=250, fillLevel=0.5, tankPressure=parameters.fuelTankPressure)  # Steel
fuelPress = MassObject(mass=0.16, length=0.072)
fuelPressTank = GasTank(
    tankVolume=250e-6,
    tankLength=0.2,
    tankMass=0.34,
    gasTemperature=parameters.fuelPressurantTemperature,
    gasType="Nitrogen",
    tankPressure=parameters.fuelPressurantTankPressure,
)

componentList = [
    engineBay,
    oxTank,
    oxPress,
    oxPressTank,
    fuelTank,
    fuelPress,
    fuelPressTank,
]

propulsionSystemLength = MassObject.calculateTotalLength(componentList)
dryMass = MassObject.calculateTotalDryMass(componentList)
wetMass = MassObject.calculateTotalMass(componentList)

fuelVolumeFlowRate = engine.fuelMassFlowRate / fuelTank.liquidDensity
oxidizerVolumeFlowRate = engine.oxMassFlowRate / oxTank.liquidDensity

engine.printParameters()
print(
    f"""  
		fuelVolumeFlow: {fuelVolumeFlowRate * 1e6:.2f} +  ml/s
		oxidizerVolumeFlow: {oxidizerVolumeFlowRate * 1e6:.2f} ml/s

	Propulsion System Parameters:
	-----------------------------
		Oxidizer mass: {oxTank.liquidMass:.3f} kg
		Fuel mass: {fuelTank.liquidMass:.3f} kg
		Oxidizer density: {oxTank.liquidDensity:.1f} kg/m³
		Fuel density: {fuelTank.liquidDensity:.1f} kg/m³
		Pressurant mass: {oxPressTank.gasMass + fuelPressTank.gasMass + oxTank.gasMass + fuelTank.gasMass:.3f} kg
		Structural mass: {MassObject.calculateTotalStructuralMass(componentList):.3f} kg
		Dry mass: {dryMass:.3f} kg
		Wet mass: {wetMass:.3f} kg
		Length: {propulsionSystemLength:.3f} m
	"""
)


timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(
    parameters.orDataFileName,
    parameters.maxBurnDuration,
    parameters.orDataReductionFactor,
)

burnTime = None
thrustList = []
thrustSum = 0
thrustNum = 0
maxThrust = 0
massList = []
cgList = []

for i in range(len(timestampList)):
    if i == 0:
        timestep = 0
    else:
        timestep = timestampList[i] - timestampList[i - 1]

    fuelMassToBurn = engine.fuelMassFlowRate * timestep
    burnedFuelMass, flownPressurantMass = fuelTank.removeLiquidMassKeepTankPressure(
        fuelMassToBurn
    )
    fuelPressTank.addGasMass(-flownPressurantMass)
    oxidizerMassToBurn = engine.oxMassFlowRate * timestep
    burnedOxMass, flownPressurantMass = oxTank.removeLiquidMassKeepTankPressure(
        oxidizerMassToBurn
    )
    oxPressTank.addGasMass(-flownPressurantMass)

    massList.append(MassObject.calculateTotalMass(componentList))
    cgList.append(propulsionSystemLength - MassObject.calculateTotalCG(componentList))

    if burnedFuelMass < fuelMassToBurn or burnedOxMass < oxidizerMassToBurn:
        thrust = 0
        if burnTime is None:
            burnTime = timestampList[i]
            print(
                f"\nburnout at t={burnTime:.2f}"
                f", remaining fuel mass: "
                f"{fuelTank.getLiquidMass() * 1000:.1f}"
                f"g, remaining oxidizer mass: "
                f"{oxTank.getLiquidMass() * 1000:.1f}g"
            )
    else:
        thrust = engine.getThrust(ambientPressureList[i] * 1e5)
        thrustNum += 1

    thrustList.append(thrust)
    thrustSum += thrust
    if thrust > maxThrust:
        maxThrust = thrust
avgThrust = thrustSum / thrustNum

if burnTime is None:
    burnTime = parameters.maxBurnDuration
    print(
        f"\nmax. burn time reached, remaining fuel mass:"
        f"{fuelTank.getLiquidMass() * 1000:.1f} g, "
        f"remaining oxidizer mass: "
        f"{oxTank.getLiquidMass() * 1000:.1f} g"
    )

orEngineFileWriter.writeEngineFile(
    burnTime,
    avgThrust,
    maxThrust,
    propulsionSystemLength,
    wetMass,
    dryMass,
    timestampList,
    cgList,
    thrustList,
    massList,
)
