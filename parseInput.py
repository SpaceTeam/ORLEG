import xmltodict
from Tanks import MassObject, GasLiquidTank, GasTank
from param_types import CEAFuelType, CEAOxidizerType, CoolPropFluid
from Engine import Engine

class Parser(object):
    def __init__(self, filePath):
        self.filePath = filePath
        self.data = None

        self.parse()

        self.generalData = self.data["rocket"]["general"]
        self.inputData = self.data["rocket"]["inputData"]
        self.componentData = self.data["rocket"]["components"]
        self.engineData = self.componentData["engine"]

    def parse(self):
        with open(self.filePath, "r") as xml_obj:
            self.data = xmltodict.parse(xml_obj.read())
            xml_obj.close()

    def generateEngine(self, fuelTankName, oxidizerTankName):
        return Engine(
            self.getEngineName(),
            CEAFuelType(self.generalData["fuelType"]),
            eval(self.componentData[fuelTankName]["liquidTemperature"]),
            CEAOxidizerType(self.generalData["oxidizerType"]),
            eval(self.componentData[oxidizerTankName]["liquidTemperature"]),
            eval(self.generalData["oxidizerFuelRatio"]),
            eval(self.engineData["chamberPressure"]),
            eval(self.generalData["referenceAmbientPressure"]),
            eval(self.engineData["referenceThrust"]),
            eval(self.generalData["engineEfficiency"]),
            eval(self.generalData["waterFraction"])
        )

    def generateLiquidTank(self, name):
        return GasLiquidTank(
            eval(self.componentData[name]["tankVolume"]),
            eval(self.componentData[name]["tankLength"]),
            eval(self.componentData[name]["tankMass"]),
            CoolPropFluid(self.generalData["oxidizerType"]),
            eval(self.componentData[name]["liquidTemperature"]),
            CoolPropFluid(self.componentData[self.componentData[name]["pressurantTank"]]["gasType"]),
            eval(self.componentData[name]["gasTemperature"]),
            eval(self.componentData[name]["fillLevel"]),
            eval(self.componentData[name]["tankPressure"])
        )
    
    def generateHeaderTank(self, name):
        return GasTank(
            eval(self.componentData[name]["tankVolume"]),
            eval(self.componentData[name]["tankLength"]),
            eval(self.componentData[name]["tankMass"]),
            CoolPropFluid(str(self.componentData[name]["gasType"])),
            eval(self.componentData[name]["gasTemperature"]),
            eval(self.componentData[name]["tankPressure"])
        )

    def generateMassObject(self, name):
        return MassObject(
            eval(self.componentData[name]["mass"]),
            eval(self.componentData[name]["length"])
        )

    def getComponents(self):
        return list(self.componentData.keys())

    def getInputName(self):
        return self.inputData["orDataFileName"]

    def getReductionFactor(self):
        return self.inputData["orDataReductionFactor"]

    def getMaxBurnDuration(self):
        return self.generalData["maxBurnDuration"]

    def getEngineManufacturer(self):
        return self.generalData["engineManufacturer"]

    def getEngineName(self):
        return self.generalData["engineName"]
    
    def getDisplayedSystemDiameter(self):
        return self.generalData["displayedSystemDiameter"]

    def getAutomaticMassCalculation(self):
        return self.generalData["automaticMassCalculation"]

    def getEnginFilePath(self):
        return "outputFiles/" + self.getEngineName() + ".rse"