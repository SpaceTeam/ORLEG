#!/usr/bin/env python3
import orSimDataReader
from Tanks import MassObject
import orEngineFileWriter
import parseInput

parser = parseInput.Parser("inputFiles/configMOCKUP.xml")

engine = parser.generateEngine("fuelTank", "oxTank")

engineBay = parser.generateMassObject("engineBay")

oxTank = parser.generateLiquidTank("oxTank")
fuelTank = parser.generateLiquidTank("fuelTank")
pressurantTank = parser.generateHeaderTank("pressurantTank")

# ToDo: Parse Components into a list (lazy) or rewrite Mass calculation
components = parser.getComponents()
componentList = []

for component in components:
    componentList.append(eval(component))

print(componentList)

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
		Pressurant mass: {pressurantTank.gasMass + pressurantTank.gasMass + oxTank.gasMass + fuelTank.gasMass:.3f} kg
		Structural mass: {MassObject.calculateTotalStructuralMass(componentList):.3f} kg
		Dry mass: {dryMass:.3f} kg
		Wet mass: {wetMass:.3f} kg
		Length: {propulsionSystemLength:.3f} m
	"""
)


timestampList, ambientPressureList, altitudeList = orSimDataReader.readORSimData(
    parser.getInputName(),
    parser.getMaxBurnDuration(),
    parser.getReductionFactor()
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
    pressurantTank.addGasMass(-flownPressurantMass)
    
    oxidizerMassToBurn = engine.oxMassFlowRate * timestep
    burnedOxMass, flownPressurantMass = oxTank.removeLiquidMassKeepTankPressure(
        oxidizerMassToBurn
    )
    pressurantTank.addGasMass(-flownPressurantMass)

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
    burnTime = parser.getMaxBurnDuration()
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
