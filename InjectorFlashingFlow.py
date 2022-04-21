#!/usr/bin/env python3
# coding=utf-8

# based on:
# https://data.space.tuwien.ac.at/index.php/apps/files/?dir=/Houbolt/Literatur&openfile=1028482 VDI Wärmeatlas L2.4/4.2 (page 1332)
# https://web.stanford.edu/~cantwell/Recent_publications/Waxman_et_al_AIAA_2013-3636.pdf

import math
import scipy.optimize as so
from CoolProp.CoolProp import PropsSI as ps
import matplotlib.pyplot as plt

# TODO: Funktion zum Massenstrom ausrechnen, Funktion zum Bohrung dimensionieren (bisect über erste Funktion), Main um mit Paper zu vergleichen

orifice_count = 4
orifice_length = 8e-3  # m
orifice_diameter = 1.5e-3  # m FIXME estimated

fluid = 'N2O'
vapor_pressure = 30e5  # Pa

tank_pressure_bar = 40  # bar
massflow_target = 0.240  # kg/s

xdot_0 = 0  # Strömungsmassengasgehalt am Einlass

Cd = 0.8  # Discharge Coefficient aus Paper


def inputvalues(tank_pressure):
	global eta_s, v_gs, v_l0, v_0, omega_frozen, omega_flash, Omega, a

	liquid_temperature = ps('T', 'Q', 1, 'P', vapor_pressure, fluid)

	if xdot_0 < 3e-3:
		gamma = xdot_0 / 3e-3
	else:
		gamma = 1

	eta_s = vapor_pressure / tank_pressure
	cp_ls = ps('C', 'Q', 0, 'T', liquid_temperature, fluid)
	v_gs = 1 / ps('D', 'Q', 1, 'T', liquid_temperature, fluid)  # m3/kg specific volume gas standard pressure
	v_g0 = 1 / ps('D', 'Q', 1, 'P', tank_pressure, fluid)  # m3/kg specific volume gas tank pressure
	v_l0 = 1 / ps('D', 'P', tank_pressure, 'T', liquid_temperature, fluid)  # m3/kg specific volume liquid tank pressure
	deltah_vs = ps('H', 'Q', 1, 'T', liquid_temperature, fluid) - ps('H', 'Q', 0, 'T', liquid_temperature, fluid)  # J/kg Verdampfungsenthalpie am Eintritt

	a = ((7.5 / ((orifice_length / orifice_diameter) + 7.5)) * (eta_s ** (-0.6))) + ((3 / 5) * gamma)
	v_0 = (xdot_0 * v_g0) + ((1 - xdot_0) * v_l0)
	# k=xdot_0/(xdot_0+((1-xdot_0)*(cp_l0/cp_gs)))
	# omega_frozen=xdot_0*(v_gs/v_0)*((1-k)+(k/(y-1))*((y**(1/k0))-1))
	omega_frozen = 0
	omega_flash = (cp_ls * liquid_temperature * tank_pressure * eta_s / v_0) * (((v_gs - v_l0) ** 2) / (deltah_vs ** 2))


def iteration(eta_crit):
	global omega
	xdot_eqth = xdot_0 + (omega_flash * (v_0 / (v_gs - v_l0)) * math.log(eta_s / eta_crit))
	omega = a * (v_0 / (v_gs - v_l0)) * (omega_flash ** 2) * (xdot_eqth ** (a - 1))
	N = xdot_eqth ** a
	omega = omega_frozen + omega_flash * N
	gamma1 = ((1 - omega) / 2) * (omega - (1 - omega))
	gamma2 = ((omega / 2) * ((2 / eta_s) - 1 - ((xdot_0 / omega_flash) * ((v_gs - v_l0) / v_0) * (1 + omega)))) + ((a / 2) * (omega - omega_frozen) * (1 + omega)) - (omega ** 2) + 1
	gamma3 = (omega * ((1 / eta_s) - 1)) - 0.5 + ((((xdot_0 / omega_flash) * ((v_gs - v_l0) / v_0)) - ((a * (omega - omega_frozen)) / omega)) * ((omega / 2) - (omega ** 2)))
	val = (eta_s * (1 + ((1 / (2 * gamma1)) * (gamma2 - math.sqrt((gamma2 ** 2) - (4 * gamma1 * gamma3)))))) - eta_crit
	return val


def getMagicValues(pressure):
	inputvalues(pressure)

	# find eta_crit iteratively
	startvalue = 1e-1
	step = 1E-3
	endvalue = startvalue + (10 * step)
	limit = 1
	while True:
		try:
			eta_crit = so.bisect(iteration, startvalue, endvalue)
			break
		except:
			startvalue += step
			endvalue += step
		if endvalue > limit:
			print("calculation failed")
			break
	C = math.sqrt((1 - eta_s) + (omega * eta_s * math.log(eta_s / eta_crit)) - ((omega - 1) * (eta_s - eta_crit))) / ((omega * ((eta_s / eta_crit) - 1)) + 1)
	#C = math.sqrt(              (omega * eta_s * math.log(eta_s / eta_crit)) - ((omega - 1) * (eta_s - eta_crit))) / ((omega * ((eta_s / eta_crit) - 1)) + 1)  # TODO VDI, warum falsch?

	return C, v_l0


if __name__ == "__main__":

	# calculate orifice size
	tank_pressure = tank_pressure_bar * 1e5
	C, v_l0 = getMagicValues(tank_pressure)
	orifice_area = (massflow_target / orifice_count) / (C * math.sqrt(2 * tank_pressure / v_l0) * Cd)
	orifice_diameter = math.sqrt(orifice_area / math.pi) * 2

	print(fluid, " vapor pressure: ", vapor_pressure * 1e-5, "bar")
	print("Diameter of", orifice_count, "orifices at ", tank_pressure_bar, "bar tank pressure:", orifice_diameter * 1e3, "mm")

	# comparison to reference measurements TODO: also add other reference values, e.g. fluid temperature (283K)
	ref_diameter = 1.5e-3
	ref_area = ((ref_diameter / 2) ** 2) * math.pi
	ref_supercharge_pressures_psi = [41, 79, 115, 169, 206, 269, 290, 329, 371]
	ref_tank_pressures = [vapor_pressure + (pressure_psi / 14.5038 * 1e5) for pressure_psi in ref_supercharge_pressures_psi]
	ref_massflows = [0.047, 0.052, 0.059, 0.067, 0.072, 0.0825, 0.085, 0.09, 0.095]

	ref_massflows_calculated = []

	for ref_pressure in ref_tank_pressures:
		C, v_l0 = getMagicValues(ref_pressure)
		ref_massflows_calculated.append(ref_area * Cd * (C * math.sqrt(2 * ref_pressure / v_l0)))

	plt.plot(ref_tank_pressures, ref_massflows_calculated, ref_tank_pressures, ref_massflows)
	plt.xlabel('supercharge pressure / bar')
	plt.ylabel('mass flow / kg/s')
	plt.grid(True)
	plt.show()
