#!/usr/bin/env python3
# coding=utf-8

import math
import pandas as pd
from scipy.integrate import trapz
import matplotlib.pyplot as plt

from Engine import Engine
from InjectorFlashingFlow import InjectorFlashingFlow
from CavitatingVenturi import CavitatingVenturi


logFile = '~/Downloads/2022-09-30_uHoubolt_static_fire_sensors.csv'


logData = pd.read_csv(logFile, sep=',', header=0)

# use time as index, sort
logData.set_index(pd.DatetimeIndex(logData['time']), inplace=True)
logData.drop(labels='time', axis='columns', inplace=True)
logData.index = logData.index - logData.index[0]
logData.sort_index(inplace=True)

# remove NaN
logData.interpolate(method='time', inplace=True)
logData.fillna(method='backfill', inplace=True)

# switch time to seconds, shift to set t=0 to start, cut
logData.index = logData.index.total_seconds()
logData.index = logData.index - 6.5  # TODO: find by first rise of some pressure
beginIndex = logData.index.get_loc(-1, method='nearest')
logData.drop(index=logData.index[:beginIndex], axis=0, inplace=True)
endIndex = logData.index.get_loc(9, method='nearest')
logData.drop(index=logData.index[endIndex:], axis=0, inplace=True)


#logData['ox_injector_pressure:sensor'] = logData['ox_tank_pressure:sensor']
#for index in logData.index:
#    logData['ox_injector_pressure:sensor'][index] = logData['ox_injector_pressure:sensor'][index] if logData['ox_injector_pressure:sensor'][index] < 48.0 else 0

logData['scale:sensor'] = logData['scale:sensor'] * 1.134 - 23.8  # korrektur nach cal

logData['scale:sensor_corr'] = logData['scale:sensor'] + 6.59 * 9.81  # raketengewicht dazu

logData['propMass'] = logData['scale:sensor_corr']
for i in range(len(logData['propMass'])):
    if logData.index[i] < 1.35:
        logData['propMass'][i] = 2.8
    elif logData.index[i] > 8.55:
        logData['propMass'][i] = 0
    else:
        logData['propMass'][i] = 2.8 - (logData.index[i] - 1.35) / (8.55 - 1.35) * 2.8

logData['scale:sensor_corr'] = logData['scale:sensor_corr'] + logData['propMass'] * 9.81  # treibstoffgewicht dazu


logData['fuel_main_valve:sensor'] *= 100 / 65535
logData['ox_main_valve:sensor'] *= 100 / 65535
logData['holddown:sensor'] *= 100 / 65535

logData['igniter0:sensor'] *= 100 / 65535
logData['igniter1:sensor'] *= 100 / 65535

#logData['ox_tank_pressure:sensor'] *= 43 / 38
#logData['ox_injector_pressure:sensor'] *= 43 / 38
#logData['fuel_tank_pressure:sensor'] *= 32 / 28
#logData['fuel_injector_pressure:sensor'] *= 32 / 28

fuelVenturi = CavitatingVenturi(fluid='ethanol', temperature=273+25, throat_diameter=1.4e-3, discharge_coefficient=0.91)
fuelMassFlows = []
for fuelInjectorPressure in logData['fuel_injector_pressure:sensor']:
    fuelMassFlows.append(fuelVenturi.getMassFlow((fuelInjectorPressure + 1) * 1e5) * 1e3 if fuelInjectorPressure > 27.45 else 0)
logData['fuel_massflow'] = fuelMassFlows

oxInjector = InjectorFlashingFlow(fluid='N2O', vapor_pressure=30e5, orifice_length=11e-3, orifice_diameter=1.6e-3, orifice_count=4, discharge_coefficient=0.78)
oxMassFlows = []
for oxInjectorPressure in logData['ox_injector_pressure:sensor']:
    oxMassFlows.append(oxInjector.getMassFlow((oxInjectorPressure + 1) * 1e5) * 1e3 if oxInjectorPressure > 35.5 else 0)
logData['ox_massflow'] = oxMassFlows

throatArea = (19e-3 / 2) ** 2 * math.pi
totalMassFlow = (logData['fuel_massflow'] + logData['ox_massflow']) * 1e-3
cStar = logData['chamber_pressure:sensor'] * 1e5 * throatArea / totalMassFlow
logData['c_star'] = cStar

fuelMass_g = trapz(logData['fuel_massflow'], logData.index)
fuelVolume_ml = fuelMass_g / fuelVenturi.density * 1e3
print("Total fuel mass:", round(fuelMass_g, 1), "g, total volume:", round(fuelVolume_ml, 1), "ml")

oxMass_g = trapz(logData['ox_massflow'], logData.index)
oxVolume_ml = oxMass_g * oxInjector.v_l0 * 1e3
print("Total ox mass:", round(oxMass_g, 1), "g, total volume:", round(oxVolume_ml, 1), "ml")

engine = Engine(name='Amalia', fuelType='Ethanol', fuelTemperature=fuelVenturi.temperature, oxidizerType="N2O", oxidizerTemperature=oxInjector.liquid_temperature, oxidizerFuelRatio=(oxMass_g / fuelMass_g), chamberPressure=15.0 * 1e5, referenceAmbientPressure=1e5, referenceThrust=650, engineEfficiency=0.8)
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

ax1 = plt.subplot(3, 1, 1)
plt.title("Actuators")

logData['fuel_main_valve:sensor'].plot(label='Fuel Main Valve / %')
logData['ox_main_valve:sensor'].plot(label='Ox Main Valve / %')
logData['holddown:sensor'].plot(label='Holddown Servo / %')

#logData['igniter0:sensor'].plot(label='Igniter 0 Current / %')
#logData['igniter1:sensor'].plot(label='Igniter 1 Current / %')

plt.grid(visible=True, which='major', axis='both', linestyle='-', color='grey')
plt.grid(visible=True, which='minor', axis='both', linestyle=':', color='grey')
plt.minorticks_on()
plt.xlim([logData.index[0], logData.index[-1]])

plt.legend()

plt.subplot(3, 1, 2, sharex=ax1)
plt.title("Pressures")

logData['fuel_tank_pressure:sensor'].plot(label='Fuel Tank Pressure / bar')
logData['ox_tank_pressure:sensor'].plot(label='Ox Tank Pressure / bar')
logData['fuel_injector_pressure:sensor'].plot(label='Fuel Injector Pressure / bar')
logData['ox_injector_pressure:sensor'].plot(label='Ox Injector Pressure / bar')
logData['chamber_pressure:sensor'].plot(label='Chamber Pressure / bar')

plt.grid(visible=True, which='major', axis='both', linestyle='-', color='grey')
plt.grid(visible=True, which='minor', axis='both', linestyle=':', color='grey')
plt.minorticks_on()
plt.xlim([logData.index[0], logData.index[-1]])

plt.legend(loc='lower left')

plt.subplot(3, 1, 3, sharex=ax1)
plt.title("Thrust")

#logData['fuel_massflow'].plot(label='Fuel Mass Flow (calculated) / g/s')
#logData['ox_massflow'].plot(label='Ox Mass Flow (calculated) / g/s')

#logData['c_star'].plot(label='C* (calculated) / m/s')

#logData['thrust'].plot(label='Thrust (calculated) / N')

logData['scale:sensor'].plot(label='Thrust Measured/ N')
logData['scale:sensor_corr'].plot(label='Thrust Corrected / N')

#logData['propMass'].plot(label='Propellant Mass')

plt.legend()
plt.grid(visible=True, which='major', axis='both', linestyle='-', color='grey')
plt.grid(visible=True, which='minor', axis='both', linestyle=':', color='grey')
plt.minorticks_on()
plt.xlim([logData.index[0], logData.index[-1]])

plt.show()
