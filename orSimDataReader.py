import inputData as vs


# OpenRocket simulation data processing
def readORSimData():
	with open(vs.inputfile, "r") as file:
		tr = []
		apr = []
		hr = []
		tl = []
		apl = []
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
			if tval >= vs.burntime > tvpre:
				tr.append(vs.burntime)  # final input rounded to given burntime, values are cut off at burnout
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
	tl.append(ts)
	apl.append(prs)
	hl.append(hs)
	count = 0  # timestamp strip
	for i in tr:
		if count == vs.stripfactor:
			tl.append(i)
			count = 0
		else:
			count += 1
	count = 0  # pressure strip
	for i in apr:
		if count == vs.stripfactor:
			apl.append(i)
			count = 0
		else:
			count += 1
	count = 0  # altitude strip
	for i in hr:
		if count == vs.stripfactor:
			hl.append(i)
			count = 0
		else:
			count += 1
	# cleansing of raw input data
	tr = None
	apr = None
	hr = None
	# ending list value input
	tl.append(te)
	apl.append(pre)
	hl.append(he)
	hn = vs.overexp * hl[-1]
	hpre = 0
	for n, i in enumerate(hl):
		if i >= hn > hpre:
			a = apl[n]
			b = apl[n - 1]
			pn = (a + b) / 2
			break
		else:
			hpre = i
	hl = None
	return pn, tl, apl
