from inputFiles import parameters


# OpenRocket simulation data processing
def readORSimData():
	with open(parameters.orDataFileName, "r") as file:
		tr = []
		apr = []
		hr = []
		timestampList = []
		ambientPressureList = []
		hl = []
		tvpre = 0
		# Extraction of Burntime, Pressure and Heigth from OR-Simulation File
		for line in file:
			data = line.split(',')
			pval = data[2]
			pval.strip('\\n')
			apr.append(float(pval) * 100)  # Conversion from mbar to pascal and pressure list input
			hval = float(data[1])
			hr.append(hval)  # altitude list input
			tval = float(data[0])
			if tval >= parameters.burnDuration > tvpre:
				tr.append(parameters.burnDuration)  # final input rounded to given burntime, values are cut off at burnout
				break
			else:
				tr.append(tval)  # timestamp list input

	# Reduction of values to desired amount
	# isolation of start and end- values (they shall not be removed in case of non-fitting stripfactor)
	ts = tr.pop(0)
	prs = apr.pop(0)
	hs = hr.pop(0)
	te = tr.pop(-1)
	pre = apr.pop(-1)
	he = hr.pop(-1)
	# first list value input
	timestampList.append(ts)
	ambientPressureList.append(prs)
	hl.append(hs)
	count = 0  # timestamp strip
	for i in tr:
		if count == parameters.orDataStripFactor:
			timestampList.append(i)
			count = 0
		else:
			count += 1
	count = 0  # pressure strip
	for i in apr:
		if count == parameters.orDataStripFactor:
			ambientPressureList.append(i)
			count = 0
		else:
			count += 1
	count = 0  # altitude strip
	for i in hr:
		if count == parameters.orDataStripFactor:
			hl.append(i)
			count = 0
		else:
			count += 1
	# cleansing of raw input data
	tr = None
	apr = None
	hr = None
	# ending list value input
	timestampList.append(te)
	ambientPressureList.append(pre)
	hl.append(he)
	hn = parameters.overexpansionRatio * hl[-1]
	hpre = 0
	for n, i in enumerate(hl):
		if i >= hn > hpre:
			a = ambientPressureList[n]
			b = ambientPressureList[n - 1]
			refAmbientPressure = (a + b) / 2
			break
		else:
			hpre = i
	hl = None
	return refAmbientPressure, timestampList, ambientPressureList
