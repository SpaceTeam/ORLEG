#!/usr/bin/env python3
# coding=utf-8

import math
import pandas as pd
from scipy.integrate import trapz
import matplotlib.pyplot as plt

from Engine import Engine
from InjectorFlashingFlow import InjectorFlashingFlow
from CavitatingVenturi import CavitatingVenturi


logFile = '~/Downloads/hotfire.csv'


logData = pd.read_csv(logFile, sep=',', header=0)

# use time as index
logData.set_index(pd.DatetimeIndex(logData['time']), inplace=True)
logData.drop(labels='time', axis='columns', inplace=True)
logData.index = logData.index - logData.index[0]

# remove NaN
logData.interpolate(method='time', inplace=True)
logData.fillna(method='backfill', inplace=True)

# switch time to seconds, cut, add offset
logData.index = logData.index.total_seconds()
N = 450*300
logData.drop(index=logData.index[:N], axis=0, inplace=True)
N = 20*300
logData.drop(logData.tail(N).index, inplace=True)
logData.index = logData.index - 451.5


logData['ox_injector_pressure:sensor'] = logData['ox_tank_pressure:sensor']
for index in logData.index:
    logData['ox_injector_pressure:sensor'][index] = logData['ox_injector_pressure:sensor'][index] if logData['ox_injector_pressure:sensor'][index] < 42.0 else 0

logData['scale:sensor'] = logData['scale:sensor'] * 0.160468920392585 - 19.2367253326063

logData['fuel_main_valve:sensor'] *= 100 / 65535
logData['ox_main_valve:sensor'] *= 100 / 65535

#logData['ox_tank_pressure:sensor'] *= 43 / 38
#logData['ox_injector_pressure:sensor'] *= 43 / 38
#logData['fuel_tank_pressure:sensor'] *= 32 / 28
#logData['fuel_injector_pressure:sensor'] *= 32 / 28

fuelVenturi = CavitatingVenturi(fluid='ethanol', temperature=273+25, throat_diameter=1.1e-3, discharge_coefficient=0.89)
fuelMassFlows = []
for fuelInjectorPressure in logData['fuel_injector_pressure:sensor']:
    fuelMassFlows.append(fuelVenturi.getMassFlow((fuelInjectorPressure + 1) * 1e5) * 1e3 if fuelInjectorPressure > 23.9 else 0)
logData['fuel_massflow'] = fuelMassFlows

oxInjector = InjectorFlashingFlow(fluid='N2O', vapor_pressure=30e5, orifice_length=11e-3, orifice_diameter=1.4e-3, orifice_count=4, discharge_coefficient=0.71)
oxMassFlows = []
for oxInjectorPressure in logData['ox_injector_pressure:sensor']:
    oxMassFlows.append(oxInjector.getMassFlow((oxInjectorPressure + 1) * 1e5) * 1e3 if oxInjectorPressure > 30.0 else 0)
logData['ox_massflow'] = oxMassFlows

throatArea = (18e-3 / 2) ** 2 * math.pi
totalMassFlow = (logData['fuel_massflow'] + logData['ox_massflow']) * 1e-3
cStar = logData['chamber_pressure:sensor'] * 1e5 * throatArea / totalMassFlow
logData['c_star'] = cStar

fuelMass_g = trapz(logData['fuel_massflow'], logData.index)
fuelVolume_ml = fuelMass_g / fuelVenturi.density * 1e3
print("Total fuel mass:", round(fuelMass_g, 1), "g, total volume:", round(fuelVolume_ml, 1), "ml")

oxMass_g = trapz(logData['ox_massflow'], logData.index)
oxVolume_ml = oxMass_g * oxInjector.v_l0 * 1e3
print("Total ox mass:", round(oxMass_g, 1), "g, total volume:", round(oxVolume_ml, 1), "ml")

engine = Engine(name='Amalia', fuelType='Ethanol', fuelTemperature=fuelVenturi.temperature, oxidizerType="N2O", oxidizerTemperature=oxInjector.liquid_temperature, oxidizerFuelRatio=(oxMass_g / fuelMass_g), chamberPressure=11.0 * 1e5, referenceAmbientPressure=1e5, referenceThrust=500, engineEfficiency=0.81)
thrust = []
for index in logData.index:
    fuelMassFlow = logData['fuel_massflow'][index] * 1e-3
    oxMassFlow = logData['ox_massflow'][index] * 1e-3
    massFlow = fuelMassFlow + oxMassFlow
    ofRatio = oxMassFlow / fuelMassFlow if fuelMassFlow > 0 and oxMassFlow > 0 else 3
    thrust.append(engine.getThrust(massFlowRate=massFlow, oxidizerFuelRatio=ofRatio) if fuelMassFlow > 0 and oxMassFlow > 0 else 0)
logData['thrust'] = thrust


#print(logData)


fig = plt.figure()

plt.subplot(2, 1, 1)
plt.title("Pressures")

logData['fuel_tank_pressure:sensor'].plot(label='Fuel Tank Pressure / bar')
logData['ox_tank_pressure:sensor'].plot(label='Ox Tank Pressure / bar')
logData['fuel_injector_pressure:sensor'].plot(label='Fuel Injector Pressure / bar')
logData['ox_injector_pressure:sensor'].plot(label='Ox Injector Pressure / bar')
logData['chamber_pressure:sensor'].plot(label='Chamber Pressure / bar')

plt.legend()
plt.grid(visible=True, which='major', axis='both', linestyle='-', color='grey')
plt.grid(visible=True, which='minor', axis='both', linestyle=':', color='grey')
plt.minorticks_on()
plt.xlim([logData.index[0], logData.index[-1]])

logData['fuel_main_valve:sensor'].plot(label='Fuel Main Valve / %', secondary_y=True)
logData['ox_main_valve:sensor'].plot(label='Ox Main Valve / %', secondary_y=True)

plt.subplot(2, 1, 2)
plt.title("Other Values")

logData['fuel_massflow'].plot(label='Fuel Mass Flow (calculated) / g/s')
logData['ox_massflow'].plot(label='Ox Mass Flow (calculated) / g/s')

logData['c_star'].plot(label='C* (calculated) / m/s')

logData['thrust'].plot(label='Thrust (calculated) / N')

logData['scale:sensor'].plot(label='Thrust / N')

plt.legend()
plt.grid(visible=True, which='major', axis='both', linestyle='-', color='grey')
plt.grid(visible=True, which='minor', axis='both', linestyle=':', color='grey')
plt.minorticks_on()
plt.xlim([logData.index[0], logData.index[-1]])

plt.show()
