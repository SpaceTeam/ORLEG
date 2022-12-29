import parseInput

parser = parseInput.Parser("inputFiles/configMOCKUP.xml")


def writeEngineFile(
    burnTime,
    averageThrust,
    maximumThrust,
    tankLength,
    wetMass,
    dryMass,
    timestampList,
    cgList,
    thrustList,
    massList,
):
    string = (
        "<engine-database>"
        + "\n  <engine-list>"
        + "\n    <engine  "
        + 'mfg="'
        + str(parser.getEngineManufacturer())
        + '" '
        + 'code="'
        + str(parser.getEngineName())
        + '" '
        + 'Type="Liquid" '
        + 'dia="'
        + str(int(parser.getDisplayedSystemDiameter() * 1000))
        + '" '
        + 'len="'
        + str(int(tankLength * 1000))
        + '" '
        + 'initWt="'
        + str(int(wetMass * 1000))
        + '" '
        + 'propWt="'
        + str(int((wetMass - dryMass) * 1000))
        + '" '
        + 'delays="0" '
        + 'auto-calc-mass="'
        + str(parser.getAutomaticMassCalculation())
        + '" '
        + 'auto-calc-cg="0" '
        + 'avgThrust="'
        + str(averageThrust)
        + '" '
        + 'peakThrust="'
        + str(maximumThrust)
        + '" '
        + 'throatDia="0" '
        + 'exitDia="'
        + str(0 * 1000)
        + '" '
        + 'Itot="'
        + str(averageThrust * burnTime)
        + '" '
        + 'burn-time="'
        + str(burnTime)
        + '" '
        + 'massFrac="0" '
        + 'Isp="'
        + str(averageThrust * burnTime / (wetMass - dryMass) / 9.81)
        + '" '
        + 'tDiv="10" '
        + 'tStep="-1." '
        + 'tFix="1" '
        + 'FDiv="10" '
        + 'FStep="-1." '
        + 'FFix="1" '
        + 'mDiv="10" '
        + 'mStep="-1." '
        + 'mFix="1" '
        + 'cgDiv="10" '
        + 'cgStep="-1." '
        + 'cgFix="1"'
        + ">"
    )

    string += "\n      <data>"
    for n, i in enumerate(timestampList):
        string += (
            "\n        <eng-data "
            + 'cg="'
            + str(cgList[n] * 1000)
            + '" '
            + 'f="'
            + str(thrustList[n])
            + '" '
            + 'm="'
            + str(massList[n] * 1000)
            + '" '
            + 't="'
            + str(timestampList[n])
            + '"/>'
        )
    string += "\n      </data>"

    string += "\n    </engine>" + "\n  </engine-list>" + "\n</engine-database>"

    with open(parser.getEnginFilePath, "w") as file:
        file.write(string)
    print("\nOpenRocket engine file generation complete")
