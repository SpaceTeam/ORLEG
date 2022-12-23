import xmltodict
from Tanks import MassObject, GasLiquidTank, GasTank
from param_types import CEAFuelType, CEAOxidizerType, CoolPropFluid
from Engine import Engine

#opening the xml file in read mode
with open("inputFiles/configMOCKUP.xml","r") as xml_obj:
    #coverting the xml data to Python dictionary
    my_dict = xmltodict.parse(xml_obj.read())
    #closing the file
    xml_obj.close()

class Parser(object):
    def __init__(self, filePath):
        self.filePath = filePath
        self.data = None

        self.name = None
        self.manufacturer = None
        self.fuelType = None
        self.oxidizerType = None
        self.oxidizerFuelRatio = None
        self.engineEfficiency = None
        self.maxBurnDuration = None
        self.referenceThrust = None
        self.waterFraction = None
        self.automaticMassCalculation = None

        self.orData = None
        self.orDataReductionFactor = None

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
            self.generalData["engineName"],
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
        return self.componentData.keys()
    