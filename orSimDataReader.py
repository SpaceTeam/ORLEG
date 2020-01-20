# OpenRocket simulation data processing, extraction of timestamp, ambient pressure and altitude
def readORSimData(dataFileName, burnDuration, reductionFactor=10):
	timestampList = []
	ambientPressureList = []
	altitudeList = []

	with open(dataFileName, "r") as file:
		for line in file:
			data = line.split(',')

			ambientPressure = float(data[2].strip('\\n'))
			ambientPressureList.append(ambientPressure / 1000)  # mbar to bar

			altitude = float(data[1])
			altitudeList.append(altitude)  # altitude list input

			timestamp = float(data[0])
			if timestamp >= burnDuration:
				timestampList.append(burnDuration)  # final input rounded to burntime, values are cut off at burnout
				break
			else:
				timestampList.append(timestamp)  # timestamp list input

	# reduce amount of values by subsampling
	timestampListShort = []
	ambientPressureListShort = []
	altitudeListShort = []

	i = 0
	while i < len(timestampList):
		timestampListShort.append(timestampList.pop(i))
		ambientPressureListShort.append(ambientPressureList.pop(i))
		altitudeListShort.append(altitudeList.pop(i))
		i += reductionFactor

	# make sure last values are copied
	timestampListShort.append(timestampList.pop(-1))
	ambientPressureListShort.append(ambientPressureList.pop(-1))
	altitudeListShort.append(altitudeList.pop(-1))

	return timestampListShort, ambientPressureListShort, altitudeListShort
