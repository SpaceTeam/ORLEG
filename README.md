# ORLEG - OpenRocket Liquid Engine Generator

## Introduction
OpenRocket is an open source 6 degree of freedom simulation tool initially developed for high power rocketry flight simulations. Due to import regulations of commercial rocketry simulation programs (RocksimPro), OpenRocket is extensively used in the realms of european experimental- and high power rocketry. While the program itself excels in terms of intuitive handling and reasonable simulation data, there is no tool for generating custom rocket engines included in the program. Also, due to usual short burntime and low level flights, Engine Altitude Compensation is not implemented in OpenRocket. Especially for teams that are designing their own liquid- or hybrid bipropellant rocket engines, this is a huge disadvantage.

ORLEG is a program/toolbox designed for simulating liquid (hybrid not implemented yet) rocket propulsion systems and generating engine files for the use in OpenRocket and other commercial simulation software. In its current state, the python based programm is capable of calculating engine parameters, modeling and simulating the feed system, calculating mass and CG changes due to flowing propellants and pressurants and accounting for changes in engine performance due to changes in ambient pressure. Due to OpenRocket requiring fixed thrust curves, the engine performance altitude compensation has to be done iteratively.

## Usage

### Installing:
To install the required dependencies and Fortran compiler, run the install.sh script with:

```sudo chmod +x install.sh```

And then:

```./install.sh```

### General:
ORLEG.py is the main file where the model of the propulsion system is described an simulated using various classes for the system components.
System parameters are currently split between inputFiles/parameters.py and ORLEG.py, this will be unified in the future.

### Pressure Data Input:
To calculate the engine performance, which depends on the ambient air pressure, ambient pressure data is needed.
It is supplied to the program in the form of the inputFiles/pressuredata.csv file, which is generated using OpenRocket and contains timestamps, ambient pressure and altitude (unused).

### Implementing Engine in OpenRocket:
If the engine file (saved in outputFiles) is used the first time, the thrust curve needs to be imported to OpenRocket.
This can be done at the setup menu by entering the file path of the engine file.
This is only necessary, if the name of the file changes.
Thrust curve updates and changes do not need to be iimported again after altering the data file.
The Engine can now be used and found in the motor database under its manufacturer and engine name just like the default motors.
When the thrust curve file is updated, OpenRocket has to be restarted tu update the data.

### Altitude Compensation curve fitting:
In order to fit the engine thrust curve to the flight path, an iterative approach has to be used.
After simulating the flight, simulation data has to be exported as pressuredata.csv and saved to inputData.
This file must include time, altitude and ambient pressure.
Next, update the engine file by running ORLEG and use it for the next OpenRocket flight simulation.
Repeat those steps, this method usually converges after three iterations.

### Output File
As output format, the rocksim engine file (.rse) type is used.
This file is more complicated than the standard .eng file but allows for changes of center of gravity and non-constant mass change.
These features are vital for simulating liquid or hybrid rockets.
Drafts for the .rse file system can be found at the following link: http://wiki.openrocket.info/RSE_File
