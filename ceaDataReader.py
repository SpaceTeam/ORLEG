acceptancelist = ['CO', 'CO2', 'H2', 'H2O', 'O2', 'H2', 'N2']


def readCea(filename):
	with open(filename, "r") as file:
		switch = 0
		compdict = {}
		for line in file:
			a = line.split()
			b = len(a)
			if b > 2:
				if a[0] == 'T,' and a[1] == 'K':
					Tcomb = float(a[2])
				elif a[0] == 'P,' and a[1] == 'BAR':
					Pcomb = float(a[2]) * 10 ** 5
			if switch > 0:
				switch += 1
				if b > 1:
					sname = a[0]
					sname = sname.strip('*')
					for i in acceptancelist:
						if sname == i:
							sval = a[1]
							sval = float(sval.replace('-', 'e-'))
							compdict[sname] = sval
				else:
					if switch > 4:
						switch = 0
						break
			if b == 2:
				if a[0] == 'MOLE' and a[1] == 'FRACTIONS':
					switch = 1
		return Tcomb, compdict, Pcomb
