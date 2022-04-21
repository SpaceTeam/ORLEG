#!/usr/bin/env python3
# coding=utf-8

# based on:
# https://data.space.tuwien.ac.at/index.php/apps/files/?dir=/Houbolt/Literatur&openfile=1028482 VDI Wärmeatlas L2.4/4.2 (page 1332)
# https://web.stanford.edu/~cantwell/Recent_publications/Waxman_et_al_AIAA_2013-3636.pdf

import math
from builtins import float

import scipy.optimize as so
from CoolProp.CoolProp import PropsSI as ps
import matplotlib.pyplot as plt


class InjectorFlashingFlow(object):

	def __init__(self, fluid, vapor_pressure, orifice_length, orifice_diameter, orifice_count=1, discharge_coefficient=0.8, xdot_0=0):

		self.fluid = fluid
		self.vapor_pressure = vapor_pressure
		self.orifice_length = orifice_length
		self.orifice_diameter = orifice_diameter
		self.orifice_count = orifice_count
		self.discharge_coefficient = discharge_coefficient
		self.xdot_0 = xdot_0

		self.orifice_area = ((self.orifice_diameter / 2) ** 2) * math.pi

		self.liquid_temperature = ps('T', 'Q', 1, 'P', self.vapor_pressure, self.fluid)
		self.cp_ls = ps('C', 'Q', 0, 'T', self.liquid_temperature, self.fluid)
		self.v_gs = 1 / ps('D', 'Q', 1, 'T', self.liquid_temperature, self.fluid)  # m3/kg specific volume of gas at standard pressure
		self.deltah_vs = ps('H', 'Q', 1, 'T', self.liquid_temperature, self.fluid) - ps('H', 'Q', 0, 'T', self.liquid_temperature, self.fluid)  # J/kg Verdampfungsenthalpie am Eintritt

		if self.xdot_0 < 3e-3:
			self.gamma = self.xdot_0 / 3e-3
		else:
			self.gamma = 1

		self.tank_pressure = None
		self.eta_crit = None
		self.omega_flash = None
		self.omega_frozen = None
		self.v_0 = None
		self.a = None
		self.v_l0 = None
		self.eta_s = None
		self.omega = None

	def updateTankPressure(self, tank_pressure):
		self.tank_pressure = tank_pressure

		self.eta_s = self.vapor_pressure / tank_pressure
		v_g0 = 1 / ps('D', 'Q', 1, 'P', tank_pressure, self.fluid)  # m3/kg specific volume of gas at tank pressure
		self.v_l0 = 1 / ps('D', 'P', tank_pressure, 'T', self.liquid_temperature, self.fluid)  # m3/kg specific volume of liquid at tank pressure

		self.a = ((7.5 / ((self.orifice_length / self.orifice_diameter) + 7.5)) * (self.eta_s ** (-0.6))) + ((3 / 5) * self.gamma)
		self.v_0 = (self.xdot_0 * v_g0) + ((1 - self.xdot_0) * self.v_l0)
		#k = self.xdot_0 / (self.xdot_0 + ((1 - self.xdot_0) * (self.cp_l0 / self.cp_gs)))
		#self.omega_frozen = self.xdot_0 * (self.v_gs / self.v_0) * ((1 - k) + (k / (self.y - 1)) * ((self.y ** (1 / self.k0)) - 1))  # TODO VDI, warum falsch?
		self.omega_frozen = 0
		self.omega_flash = (self.cp_ls * self.liquid_temperature * tank_pressure * self.eta_s / self.v_0) * (((self.v_gs - self.v_l0) ** 2) / (self.deltah_vs ** 2))

		#try:
		#	self.eta_crit = so.bisect(self.iteration, 0.1, 1, maxiter=1000)
		#except:
		#	print("finding eta_crit failed")
		#	exit()

		# find eta_crit iteratively TODO: set better start/end values, don't iterate like above)?
		startvalue = 1e-1
		step = 1e-3
		endvalue = startvalue + (10 * step)
		limit = 1
		while True:
			try:
				self.eta_crit = so.bisect(self.iteration, startvalue, endvalue)
				break
			except:
				startvalue += step
				endvalue += step

			if endvalue > limit:
				print("finding eta_crit failed")
				exit()

	def iteration(self, eta_crit):
		xdot_eqth = self.xdot_0 + (self.omega_flash * (self.v_0 / (self.v_gs - self.v_l0)) * math.log(self.eta_s / eta_crit))
		N = xdot_eqth ** self.a
		self.omega = self.omega_frozen + self.omega_flash * N
		Omega = self.a * (self.v_0 / (self.v_gs - self.v_l0)) * (self.omega_flash ** 2) * (xdot_eqth ** (self.a - 1))
		Gamma1 = ((1 - self.omega) / 2) * (Omega - (1 - self.omega))
		Gamma2 = ((Omega / 2) * ((2 / self.eta_s) - 1 - ((self.xdot_0 / self.omega_flash) * ((self.v_gs - self.v_l0) / self.v_0) * (1 + self.omega)))) + ((self.a / 2) * (self.omega - self.omega_frozen) * (1 + self.omega)) - (self.omega ** 2) + 1
		Gamma3 = (self.omega * ((1 / self.eta_s) - 1)) - 0.5 + ((((self.xdot_0 / self.omega_flash) * ((self.v_gs - self.v_l0) / self.v_0)) - ((self.a * (self.omega - self.omega_frozen)) / Omega)) * ((Omega / 2) - (self.omega ** 2)))
		return (self.eta_s * (1 + ((1 / (2 * Gamma1)) * (Gamma2 - math.sqrt((Gamma2 ** 2) - (4 * Gamma1 * Gamma3)))))) - eta_crit  # subtract eta_crit to make function return zero when correct eta_crit found

	def getMassFlow(self, tank_pressure):
		self.updateTankPressure(tank_pressure)

		C = math.sqrt((1 - self.eta_s) + (self.omega * self.eta_s * math.log(self.eta_s / self.eta_crit)) - ((self.omega - 1) * (self.eta_s - self.eta_crit))) / ((self.omega * ((self.eta_s / self.eta_crit) - 1)) + 1)
		# C = math.sqrt(              (omega * eta_s * math.log(eta_s / eta_crit)) - ((omega - 1) * (eta_s - eta_crit))) / ((omega * ((eta_s / eta_crit) - 1)) + 1)  # TODO VDI, warum falsch?

		return self.orifice_count * self.orifice_area * self.discharge_coefficient * C * math.sqrt(2 * tank_pressure / self.v_l0)


if __name__ == "__main__":

	# calculate mass flow
	injector = InjectorFlashingFlow(fluid='N2O', vapor_pressure=30e5, orifice_length=11e-3, orifice_diameter=1.4e-3, orifice_count=4, discharge_coefficient=0.8)
	massFlow = injector.getMassFlow(tank_pressure=40e5)
	print("mass flow with", injector.orifice_count, "orifices of", injector.orifice_diameter * 1e3, "mm diameter at", injector.tank_pressure * 1e-5, "bar tank pressure:", round(massFlow, 3), "kg/s")

	# TODO funktion zum Bohrung dimensionieren (bisect über Massenstrom?)
#	tank_pressure = tank_pressure_bar * 1e5
#	C, v_l0 = getMagicValues(tank_pressure)
#	orifice_area = (massflow_target / orifice_count) / (C * math.sqrt(2 * tank_pressure / v_l0) * Cd)
#	orifice_diameter = math.sqrt(orifice_area / math.pi) * 2
#	print("Diameter of", orifice_count, "orifices at ", tank_pressure_bar, "bar tank pressure:", orifice_diameter * 1e3, "mm")

	# comparison to reference measurements (from paper linked above)
	referenceInjector = InjectorFlashingFlow(fluid='N2O', vapor_pressure=40e5, orifice_length=18.4e-3, orifice_diameter=1.5e-3, orifice_count=1, discharge_coefficient=0.8)

	ref_supercharge_pressures_psi = [41, 79, 115, 169, 206, 269, 290, 329, 371]
	ref_massflows = [0.047, 0.052, 0.059, 0.067, 0.072, 0.0825, 0.085, 0.09, 0.095]

	ref_tank_pressures = [referenceInjector.vapor_pressure + (pressure_psi / 14.5038 * 1e5) for pressure_psi in ref_supercharge_pressures_psi]

	ref_massflows_calculated = []

	for ref_tank_pressure in ref_tank_pressures:
		ref_massflows_calculated.append(referenceInjector.getMassFlow(ref_tank_pressure))

	plt.plot(ref_tank_pressures, ref_massflows_calculated, ref_tank_pressures, ref_massflows)
	plt.xlabel('tank pressure / Pa')
	plt.ylabel('mass flow / kg/s')
	plt.grid(True)
	plt.show()
