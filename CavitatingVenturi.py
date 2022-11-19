#!/usr/bin/env python3
# coding=utf-8

import math
from CoolProp.CoolProp import PropsSI as ps


class CavitatingVenturi(object):
    def __init__(self, fluid, temperature, throat_diameter, discharge_coefficient):
        self.fluid = fluid
        self.temperature = temperature
        self.throat_diameter = throat_diameter
        self.discharge_coefficient = discharge_coefficient

        self.vapor_pressure = ps("P", "Q", 1, "T", self.temperature, self.fluid)
        self.throat_area = ((self.throat_diameter / 2) ** 2) * math.pi
        self.density = ps("D", "P", 1e5, "T", self.temperature, self.fluid)

    def getMassFlow(self, pressure):
        self.density = ps("D", "P", pressure, "T", self.temperature, self.fluid)
        return (
            self.discharge_coefficient
            * self.throat_area
            * math.sqrt(2 * self.density * (pressure - self.vapor_pressure))
        )


if __name__ == "__main__":

    venturi = CavitatingVenturi(
        fluid="ethanol",
        temperature=273 + 25,
        throat_diameter=1.0e-3,
        discharge_coefficient=0.87,
    )

    pressure_bar = 30
    massFlow = venturi.getMassFlow(pressure_bar * 1e5)

    print(
        "mass flow with",
        venturi.throat_diameter * 1e3,
        "mm diameter venturi at",
        pressure_bar,
        "bar upstream pressure:",
        round(massFlow, 3),
        "kg/s",
    )
