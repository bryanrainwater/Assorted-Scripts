from common.libraryImports import *

###FILE MANIPULATION###
def jdProcessor(jsecs, jusecs):
    jd = np.array([0.0 for x in jsecs])
    offset = gcal2jd(1970, 1, 1)[0] - 0.5 + gcal2jd(1970, 1, 1)[1]
    for i, (jsec, jusec) in enumerate(zip(jsecs, jusecs)):
        jd[i] = offset + jsec / (60.0 * 60.0 * 24.0) + (jusec * (1.0e-6)) / 86400.0
    return jd


def jd2secs(jd, dateString="19700101"):
    # dateString must be YYYYMMDD as a string
    seconds = (
        jd
        - gcal2jd((dateString[0:4]), (dateString[4:6]), (dateString[6:8]))[0]
        - gcal2jd((dateString[0:4]), (dateString[4:6]), (dateString[6:8]))[1]
    ) * 86400
    return seconds


def dateFromFileName(filePath):
    dateString = filePath.split("/")[-1]
    dateString = dateString.split("_")[0]
    dateString = dateString.split("-")[1]
    dateString = dateString.split("_")[0]
    return dateString


def laserFilter(data, dual=True, lNum=1):
    if dual:
        data["lNum"] = np.ones(len(data["press"])) * 3
        data["scan1"] = data["scans"][:, 0:1024]
        data["scan2"] = data["scans"][:, 1024:]
        for i in range(512):
            data["scan1"][:, i] = np.mean(data["scans"][:, i * 2 : (i + 1) * 2], axis=1)
            data["scan2"][:, i] = np.mean(
                data["scans"][:, i * 2 + 1024 : (i + 1) * 2 + 1024], axis=1
            )
            data["scan1"] = data["scan1"][:, :512]
            data["scan2"] = data["scan2"][:, :512]
    else:
        data["lNum"] = np.ones(len(data["press"])) * lNum
    return data


def mergefiles(files):
    """File merging routine.

	Used to merge disjointed files of the same type.

	inputs:
		files: Array containing list of files with
			that can be appended with _HK or _SC.

	outputs:
		two element array containing two merged filenames
	"""

    filestomerge = []
    for file in files:
        if "_HK" in file[-3:]:
            tmpstring = [s for s in files if file[:-3] + "_SC" == s]
            if len(tmpstring) == 1:
                filestomerge.append(file)
                filestomerge.append(tmpstring[0])

    mergedfiles = []
    if len(filestomerge) > 2:
        mergedfiles.append(str(filestomerge[0]) + "_merged")
        mergedfiles.append(str(filestomerge[1]) + "_merged")
    else:
        return files

    HKout = []
    SCout = []
    # self.progress.setRange(0,round(len(filestomerge)/2))
    # self.progress.setValue(0)
    for i in range(round(len(filestomerge) / 2)):
        with open(filestomerge[round(2 * i)], "rb") as infile:
            HKheader = np.fromfile(infile, np.int32, 7)
            try:
                numHK = HKheader[0]
            except:
                continue
            HKraw = np.fromfile(infile, np.int32)
        with open(filestomerge[round(2 * i) + 1], "rb") as infile:
            SCheader = np.fromfile(infile, np.int32, 8)
            try:
                numSC = SCheader[0]
            except:
                continue
            SCraw = np.fromfile(infile, np.int32)
        ctLineHK = round(numHK + 2)
        nrecsHK = math.floor(len(HKraw) / float(ctLineHK))

        ctLineSC = round(numSC + 2)
        nrecsSC = math.floor(len(SCraw) / float(ctLineSC))

        HKraw = HKraw[: math.floor(nrecsHK) * ctLineHK]
        SCraw = SCraw[: math.floor(nrecsSC) * ctLineSC]

        # Potentially add check above for if the length of HKraw is less than math.floor(nrecsHK)*ctLineHK
        # otherwise it needs to just continue onto the next line

        # HKtest = np.reshape(HKraw,(nrecsHK,ctLineHK))#(ctLine,nrecs))
        # print(np.array(HKtest[:,0]))
        # print(np.array(HKtest[:,1]))
        # input('seconds and microseconds pause')

        if i == 0:
            with open(mergedfiles[0], "wb") as outfile:
                outfile.write(HKheader)
                HKraw.tofile(outfile)
            with open(mergedfiles[1], "wb") as outfile:
                outfile.write(SCheader)
                SCraw.tofile(outfile)
        else:
            with open(mergedfiles[0], "ab") as outfile:
                HKraw.tofile(outfile)
            with open(mergedfiles[1], "ab") as outfile:
                SCraw.tofile(outfile)
        # self.progress.setValue(i+1)
        # self.progress.setValue((i+1)*int(100/round(len(filestomerge)/2)))
    return mergedfiles


def readHK(file, newFmt=False, saveCSV=False, extractTimes=None):
    """Read Housekeeping data.

	Used to read housekeeping data from binary or csv file.

	inputs:
		file: filepath for HK file.
		newFmt: bool, false = binary, true = csv
		saveCSV: For saving raw binary data to a csv file
		extractTimes: 2 element array containing YYYYMMDD_hhmmss
			for start and end time bounds to limit read.
	outputs:
		dictionary with housekeeping data.
	"""

    if not newFmt:
        with open(file, "rb") as infile:
            numHK = (np.fromfile(infile, np.int32, 1))[0]
            tmparray = np.fromfile(infile, np.float32, 4)
            MFCset = tmparray[0]
            vStart = tmparray[1]
            vEnd = tmparray[2]
            vMod = tmparray[3]
            tmparray = np.fromfile(infile, np.int32, 2)
            pp2fEnable = tmparray[0]
            minsPerFile = tmparray[1]
            HKraw = np.fromfile(infile, np.int32)
    else:
        MFCset = 0
        vStart = 0
        vEnd = 0
        vMod = 0
        pp2fEnable = 0
        minsPerFile = 0

        lineCnt = 0
        HKraw = []
        with open(file, "r") as scanFile:
            for line in scanFile:
                if lineCnt == 1:
                    DAChannels = int(line.split(",")[0].split(":")[-1])
                elif lineCnt == 2:
                    ADChannels = int(line.split(",")[0].split(":")[-1])
                elif lineCnt == 3:
                    bufferSize = int(line.split(",")[0].split(":")[-1])
                # numHK = int(line.split(':')[-1])
                elif lineCnt == 5:
                    numHK = len(line.split(",")) - 2
                    try:
                        HKraw.extend([float(x) for x in line.split(",")])
                    except:
                        pass
                elif lineCnt > 5:
                    try:
                        HKraw.extend([float(x) for x in line.split(",")])
                    except:
                        pass
                lineCnt += 1

    ctLine = round(numHK + 2)
    nrecs = math.floor(len(HKraw) / float(ctLine))

    HKraw = HKraw[: math.floor(nrecs) * ctLine]

    HKraw = np.reshape(HKraw, (nrecs, ctLine))  # (ctLine,nrecs))

    # if self.extractTimes:
    if extractTimes is not None:
        startText = extractTimes[0]
        endText = extractTimes[1]
        # if self.extractTimes:
        # 	startText = self.startTime.text()
        # 	endText = self.endTime.text()

        startTime = (
            gcal2jd(startText[0:4], startText[4:6], startText[6:8])[1] * 86400.0
            + int(startText[9:11]) * 60.0 * 60.0
            + int(startText[11:13]) * 60.0
            + int(startText[13:15])
        )
        endTime = (
            gcal2jd(endText[0:4], endText[4:6], endText[6:8])[1] * 86400.0
            + int(endText[9:11]) * 60.0 * 60.0
            + int(endText[11:13]) * 60.0
            + int(endText[13:15])
        )

        startTime = startTime - gcal2jd(1970, 1, 1)[1] * 86400.0
        endTime = endTime - gcal2jd(1970, 1, 1)[1] * 86400.0

        validTimes = np.where(
            np.logical_and(
                np.greater_equal(np.array(HKraw[:, 0]), startTime),
                np.less_equal(np.array(HKraw[:, 0]), endTime),
            )
        )
        nrecs = len(validTimes[0])
        HKraw = HKraw[validTimes[0], :]
        # HKraw = HKraw[:]

    seconds = np.array(HKraw[:, 0])
    microseconds = np.array(HKraw[:, 1])  # ,:]

    # Line below replaces above for JPL experiment
    # HKdata = 5.0*(HKraw[:,2:]/32767)#,:]+32767)/65535

    jd = jdProcessor(seconds, microseconds)

    # Tells me the year, month, and day of the data
    # jdDate = jd2gcal(
    #    gcal2jd(1970, 1, 1)[0],
    #    np.floor(seconds[0] / (3600 * 24)) + gcal2jd(1970, 1, 1)[1],
    # )
    # for i in range(nrecs):
    #    jd[i] = gcal2jd(jdDate[0], jdDate[1], jdDate[2])[1] - gcal2jd(1970, 1, 1)[1]
    #    jd[i] = seconds[i] - int(3600 * 24 * jd[i])  # + microseconds[i]*1e-6

    if not newFmt:
        HKdata = 5.0 * (HKraw[:, 2:] + 32767) / 65535  # ,:]+32767)/65535
        temps = (HKdata[:, 3:6] ** 2) * 137.68 - HKdata[:, 3:6] * 498.74 + 387.8
        temps[:, 2] = temps[:, 2] + 2.0
        # temps = ((HKdata[:,3:6]))
        press = HKdata[:, 6] * 290.22 - 3.3685
        MFC = HKdata[:, 11] * 2.0
        # current = HKdata[:,10]
        current = HKdata[:, 7] / 20

        HK = {
            "juldate": jd,
            "PD": HKdata[:, 0],
            "tdetect": HKdata[:, 1],
            "tlaser": HKdata[:, 2],
            "temp1": temps[:, 0],
            "tbody": temps[:, 1],
            "temp2": temps[:, 2],
            "press": press,
            "current": current,
            "vlaser": HKdata[:, 8],
            "MFC": MFC,
        }

    else:
        HKdata = HKraw[:, 2:]
        numScansAvgd = HKdata[:, 0]
        numScansLost = HKdata[:, 1]
        """
		numScansAvgd = HKdata[:,0]
		numScansLost = HKdata[:,1]
		# press = 10.0*(HKdata[:,5]/5.0 + 0.095)/0.009

		# June 19, 2018 Pressure Cal m = 222.38935, b = 114.06569
		press = (HKdata[:,5]*222.38935) + 114.06569
		temps = HKdata[:,2:5]#*0 + 25.0
		MFC = HKdata[:,6]*0 + 3.0
		current = HKdata[:,6]*0 + 3.0

		temps[:,0] = 30000.0*((5.0/temps[:,2])-1.0)
		temps[:,0] = 1.0/(1/298.15 + (1/3810.0)*np.log(temps[:,0]/30000.0)) - 273.15
		"""
        newer = True
        if newer:
            # June 19, 2018 Pressure Cal m = 222.38935, b = 114.06569
            press = HKdata[:, 9]  # *222.38935) + 114.06569
            temps = HKdata[:, 6:9]  # *0 + 25.0
            MFC = HKdata[:, 6] * 0 + 3.0
            current = HKdata[:, 6] * 0 + 3.0

            HK = {
                "juldate": jd,
                "PD": HKdata[:, 0],
                "tdetect": HKdata[:, 1],
                "tlaser": HKdata[:, 2],
                "l1Temp": temps[:, 0],
                "l2Temp": temps[:, 1],
                "cellTemp": temps[:, 2],
                "press": press,
                "current": current,
                "vlaser": HKdata[:, 8],
                "MFC": MFC,
                "dark": HKdata[:, 5],
                "lPstart": HKdata[:, 2],
                "lPend": HKdata[:, 3],
                "avgNum": HKdata[:, 0],
            }
        else:
            # June 19, 2018 Pressure Cal m = 222.38935, b = 114.06569
            press = (HKdata[:, 5] * 222.38935) + 114.06569
            temps = HKdata[:, 2:5]  # *0 + 25.0
            MFC = HKdata[:, 6] * 0 + 3.0
            current = HKdata[:, 6] * 0 + 3.0

            temps[:, 0] = 30000.0 * ((5.0 / temps[:, 2]) - 1.0)
            temps[:, 0] = (
                1.0 / (1 / 298.15 + (1 / 3810.0) * np.log(temps[:, 0] / 30000.0)) - 273.15
            )

            HK = {
                "juldate": jd,
                "PD": HKdata[:, 0],
                "tdetect": HKdata[:, 1],
                "tlaser": HKdata[:, 2],
                "temp1": temps[:, 0],
                "tbody": temps[:, 1],
                "temp2": temps[:, 2],
                "press": press,
                "current": current,
                "vlaser": HKdata[:, 8],
                "MFC": MFC,
            }

    HKDesc = copy.deepcopy(HK)
    HKDesc["juldate"] = "Julian Date"
    HKDesc["PD"] = "Photodetector Current"
    HKDesc["tdetect"] = "Detector Temperature (C)"
    HKDesc["tlaser"] = "Laser Temperature (C)"
    HKDesc["temp1"] = "Cell Temperature 1 (C)"
    HKDesc["temp2"] = "Cell Temperature 2 (C)"
    HKDesc["tbody"] = "Body Temperature (C)"
    HKDesc["press"] = "Cell Pressure (mbar)"
    HKDesc["current"] = "Average current from photodiode"
    HKDesc["vlaser"] = "Average lsaer power"
    HKDesc["MFC"] = "Mass flow controller flow (SLPM)"

    if saveCSV:
        with open(file + ".csv", "wb") as csvfile:
            # datestring = ''.join(''.join(''.join(str(file).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
            datestring = "".join(
                "".join("".join(str(file).split("/")[-1:]).split("-")[-1:]).split("_")[0]
            )
            datestring = "".join(datestring.split("_")[0])
            seconds = np.round(
                (
                    jd
                    - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[0]
                    - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[1]
                )
                * 86400.0
                + 1
            )

            # np.savetxt(csvfile, np.c_[seconds+microseconds*1e-6,HKdata],fmt = '%.6f',delimiter = ',', newline = '\r\n', header = 'seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC')
            np.savetxt(
                csvfile,
                np.c_[
                    seconds + microseconds * 1e-6,
                    HKdata[:, :3],
                    temps,
                    press,
                    current,
                    HKdata[:, 8],
                    MFC,
                ],
                fmt="%.6f",
                delimiter=",",
                newline="\r\n",
                header="seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC",
            )

    # if self.pickleSave:
    # 	self.pickleDict['HK'] = np.c_[HKdata[:,:3],temps,press,current,HKdata[:,8],MFC]

    return [HK, HKDesc]
    # plt.plot(jd, HKdata[:,3])#)#[:,0])
    # plt.show()


def readSC(file, newFmt=False, saveCSV=False, extractTimes=None):
    """Read scan data.

	Used to read scan data from binary or csv file.

	inputs:
		file: filepath for SC file.
		newFmt: bool, false = binary, true = csv
		saveCSV: For saving raw binary data to a csv file
		extractTimes: 2 element array containing YYYYMMDD_hhmmss
			for start and end time bounds to limit read.
	outputs:
		dictionary with scan data.
	"""

    if not newFmt:
        with open(file, "rb") as infile:
            numSC = (np.fromfile(infile, np.int32, 1))[0]
            numDark = (np.fromfile(infile, np.int32, 1))[0]
            tmparray = np.fromfile(infile, np.float32, 4)
            MFCset = tmparray[0]
            vStart = tmparray[1]
            vEnd = tmparray[2]
            vMod = tmparray[3]
            tmparray = np.fromfile(infile, np.int32, 2)
            pp2fEnable = tmparray[0]
            minsPerFile = tmparray[1]
            SCraw = np.fromfile(infile, np.int32)

    else:
        numDark = 45
        MFCset = 0
        vStart = 0
        vEnd = 0
        vMod = 0
        pp2fEnable = 0
        minsPerFile = 0

        lineCnt = 0
        SCraw = []

        offset = 4

        try:
            with open(file, "r") as scanFile:
                for i, line in enumerate(scanFile):
                    # print(line)
                    if i == offset + 4:
                        laserNum = int(line.split(",")[0].split(":")[-1])
                        break
        except:
            offset = 3

        with open(file, "r") as scanFile:
            for line in scanFile:
                if lineCnt == offset:
                    outrate = int(line.split(",")[0].split(":")[-1])
                if lineCnt == offset + 1:
                    DAChannels = int(line.split(",")[0].split(":")[-1])
                elif lineCnt == offset + 2:
                    ADChannels = int(line.split(",")[0].split(":")[-1])
                elif lineCnt == offset + 4:
                    numSC = int(line.split(",")[0].split(":")[-1])
                elif lineCnt == offset + 3:
                    laserNum = int(line.split(",")[0].split(":")[-1])
                elif lineCnt >= offset + 5:
                    try:
                        SCraw.extend([float(x) for x in line.split(",")])
                    except:
                        pass
                lineCnt += 1

    ctLine = round(numSC + 2)
    nrecs = math.floor(len(SCraw) / float(ctLine))

    SCraw = SCraw[: math.floor(nrecs) * ctLine]
    SCraw = np.reshape(SCraw, (nrecs, ctLine))  # (ctLine,nrecs))

    # if self.extractTimes:
    if extractTimes is not None:
        startText = extractTimes[0]
        endText = extractTimes[1]
        # startText = self.startTime.text()
        # endText = self.endTime.text()

        startTime = (
            gcal2jd(startText[0:4], startText[4:6], startText[6:8])[1] * 86400
            + int(startText[9:11]) * 60 * 60
            + int(startText[11:13]) * 60
            + int(startText[13:15])
        )
        endTime = (
            gcal2jd(endText[0:4], endText[4:6], endText[6:8])[1] * 86400
            + int(endText[9:11]) * 60 * 60
            + int(endText[11:13]) * 60
            + int(endText[13:15])
        )

        startTime = startTime - gcal2jd(1970, 1, 1)[1] * 86400
        endTime = endTime - gcal2jd(1970, 1, 1)[1] * 86400

        validTimes = np.where(
            np.logical_and(
                np.greater_equal(np.array(SCraw[:, 0]), startTime),
                np.less_equal(np.array(SCraw[:, 0]), endTime),
            )
        )
        nrecs = len(validTimes[0])
        SCraw = SCraw[validTimes[0], :]

    seconds = np.array(SCraw[:, 0])  # ,:]
    microseconds = np.array(SCraw[:, 1])  # ,:]

    if not newFmt:
        SCdata = 10.0 * (SCraw[:, 2:]) / 65535.0  # ,:]+32767)/65535
    else:
        SCdata = SCraw[:, 2:]

    # Correction to remove half of spectra
    # SCdata = SCdata[:,:(int)(numSC/2)]
    # SCdata = SCdata[:,:(int)(numSC/2)]
    # numSC = (int)(numSC/2)
    # numSC = (int)(numSC/2)

    # SCdata = 5.0*(SCraw[:,2:])/65535.0#,:]+32767)/65535

    """
    jd = np.array([0.0 for x in seconds])
    # Can subtract 0.5 from the offset in order to be seconds from beginnig of the day
    offset = gcal2jd(1970, 1, 1)[0] - 0.5 + gcal2jd(1970, 1, 1)[1]
    # offset = gcal2jd(1970,1,1)[0] +gcal2jd(1970,1,1)[1]
    for i in range(nrecs):
        jd[i] = (
            offset
            + seconds[i] / (60.0 * 60.0 * 24.0)
            + (microseconds[i] * (1.0e-6)) / 86400.0
        )
    """
    jd = jdProcessor(seconds, microseconds)

    if saveCSV:
        with open(file + ".csv", "wb") as csvfile:
            # np.savetxt(csvfile, 'hello')
            # datestring = ''.join(''.join(''.join(str(file).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
            datestring = "".join(
                "".join("".join(str(file).split("/")[-1:]).split("-")[-1:]).split("_")[0]
            )
            datestring = "".join(datestring.split("_")[0])
            seconds = np.round(
                (
                    jd
                    + 0.5
                    - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[0]
                    - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[1]
                )
                * 86400
                + 1
            )

            np.savetxt(
                csvfile,
                np.arange(1024).reshape(1, np.arange(1024).shape[0]),
                fmt="%d",
                delimiter=",",
                newline="\r\n",
            )
            np.savetxt(
                csvfile,
                np.c_[seconds + microseconds * 1e-6, SCdata],
                fmt="%.6f",
                delimiter=",",
                newline="\r\n",
            )

    # if self.pickleSave:
    # 	self.pickleDict['SC'] = SCdata

    SC = {"juldate": jd, "scans": SCdata}
    if newFmt:
        SC["lNum"] = np.ones(len(jd)) * laserNum
    SCDesc = copy.deepcopy(SC)
    SCDesc["juldate"] = "Julian Date"
    SCDesc["scans"] = "Raw Spectral Scans (V)"
    # plt.plot(np.arange(numSC), SC['scans'][0,:])#)#[:,0])
    # plt.show()
    return [SC, SCDesc]


def fixjuldate(input):
    """Julian data correction routine.

	Used to correct discontinous negative jumps in time.

	Input: injected array with julian date
	output: corrected array
	"""

    output = copy.deepcopy(input)
    # seconds = (input - math.floor(input[0])+0.5)*3600*24
    seconds = (input - math.floor(input[0])) * 3600 * 24
    leftptr = 1
    flagptr = 1
    rightptr = len(input)
    obs = len(input) - 1
    for i in range(obs):
        delta = seconds[i] - seconds[i - 1]
        if delta <= 0:
            flagptr = i
        if delta >= 2 or i == len(input) - 2:
            rightptr = i
            if flagptr > 1:
                correction = output[flagptr] - output[flagptr - 1]
                correction -= (output[rightptr - 1] - output[flagptr]) / (
                    rightptr - flagptr + 1
                )
                output[leftptr - 1 : flagptr - 1] = (
                    output[leftptr - 1 : flagptr - 1] + correction
                )
            leftptr = i + 1
            rightptr = i + 1

    return output


def averageData(HK, SC, Hz=1, runAvgSize=1, newFmt=False):
    """Data averaging routine.

	Used to

	inputs:
		HK: Housekeeping dictionary
		SC: Scan dictionary
		Hz: Desired output frequency
		runAvgSize: Unsure at the moment.

	outputs: Tuple with output HK and SC data at
		desired output frequency.
	"""

    # input('entered averageonehz function')
    # seconds = (SC['juldate'] - np.floor(SC['juldate'][0])+0.5)*3600.0*24.0#+0.5)*3600*24
    # HKseconds = (HK['juldate'] - np.floor(HK['juldate'][0])+0.5)*3600.0*24.0
    seconds = (
        (SC["juldate"] - np.floor(SC["juldate"][0])) * 3600.0 * 24.0
    )  # +0.5)*3600*24
    HKseconds = (HK["juldate"] - np.floor(HK["juldate"][0])) * 3600.0 * 24.0

    # Revision 7-22-19 to just use Julian secs and usecs for histogram binning
    #   instead of converting to seconds and then back.
    # HKseconds = HK["juldate"]
    # seconds = SC["juldate"]

    start = math.ceil(min(seconds))
    stop = math.floor(max(seconds))

    if newFmt:  # self.newFmt:
        start = int(start + 5.0)

    # Code added to fix precision issue where repeating digits appeared for seemingly simple solutions... i.e. 0.2 = 0.199999999...
    precision = 0
    for i in range(5):
        if np.round(0.5 / Hz, precision) == 0.5 / Hz:
            break
        precision += 1

    # print(np.round(np.arange(start-0.5/Hz, stop+0.5/Hz, 1/Hz), precision), start, stop)
    # input('wait')

    histBins = np.round(np.arange(start - 0.5 / Hz, stop + 0.5 / Hz, 1 / Hz), precision)

    # [hist,histval] = np.array(np.histogram(seconds,np.round(np.arange(start-0.5/Hz,stop+0.5/Hz,1/Hz),precision)))
    # SCindices = np.digitize(seconds, np.round(np.arange(start-0.5/Hz, stop+0.5/Hz, 1/Hz), precision))
    # scanint = np.zeros((len(hist),dims[1]))
    # scanint = np.zeros((len(hist),dims[1]))

    # input('created seconds array')
    # secsOut = start+np.arange(nsteps)
    # secsOut = histval[:-1] + 0.5/Hz##start+np.round(np.arange(0,stop-start+1,1/Hz),precision)
    # secsOut = stop + 0.5/Hz##start+np.round(np.arange(0,stop-start+1,1/Hz),precision)
    secsOut = histBins + 0.5 / Hz

    # self.seconds = secsOut
    #seconds = secsOut

    if len(secsOut) > 10000000:
        print("Array WAYYYY too large.... exiting now")
        return

    # juldate = secsOut/(3600*24)-(0.5/Hz)+float(math.floor(SC['juldate'][0]))
    # juldate = secsOut/(3600*24)-(2/Hz)+float(math.floor(SC['juldate'][0]))
    juldate = secsOut / (3600 * 24) + 0.5 + float(math.floor(SC["juldate"][0]))
    # juldate = secsOut/(3600*24)+float(math.floor(SC['juldate'][0]))
    # juldate = secsOut/(3600*24)-0.5+float(math.floor(SC['juldate'][0]))

    # SET THESE AS RETURN PARAMETERS
    # self.startTime.setText(startText)
    # self.endTime.setText(endText)

    # self.numObservations.setText(str(len(hist)))
    # self.numObservations.setText(str(len(secsOut)))
    # self.plotDivisions.setText(str(len(hist)))
    # self.plotDivisions.setText(str(len(secsOut)))

    # tmparray = secsOut#[math.floor(x) for x in seconds]
    # tmp, un_ind = np.unique(tmparray, return_index = True)

    # Returns a true/false mask of length of first arg if elements are in
    # histmask = np.in1d(histval, tmp)

    # j = 0
    # mask = []
    # for i in range(len(histval)):
    # 	if not histmask[i]:# or j >= len(tmp):
    # 		mask.append(0)
    # 		continue
    # 	while True:
    # 		if histval[i] == tmp[j]:
    # 			mask.append(un_ind[j])
    # 			break
    # 		else: j+=1

    # self.progress.setRange(0,len(hist)-1)
    obs = len(secsOut)
    # self.progress.setRange(0,len(secsOut))
    # self.progress.setValue(0)

    # if round(i*100/obs) == i/np.floor(obs/100):
    # runningAvg = 0.2

    # [hist,histval] = np.array(np.histogram(seconds,np.round(np.arange(start-0.5/Hz,stop+0.5/Hz,1/Hz),precision)))
    # [HKhist, HKhistval] = np.array(np.histogram(HKseconds, np.round(np.arange(start-0.5/Hz, stop+0.5/Hz, 1/Hz), precision)))
    # HKindices = np.digitize(HKseconds, np.round(np.arange(start-0.5/Hz, stop+0.5/Hz, 1/Hz), precision))
    dims = SC["scans"].shape

    SCindices = np.array(np.digitize(seconds, histBins))
    HKindices = np.array(np.digitize(HKseconds, histBins))

    # scanint = np.zeros((len(secsOut),dims[1]))

    # scanint = SC

    # binnedHK = np.zeros(len(histBins)+1, 10)
    # binnedHK = HK.copy()
    # binnedHK = dict(HK)
    # binnedHK = HK.copy.deepcopy()
    # binnedHK = copy.deepcopy(HK)
    binnedHK = dict()

    keysToSum = ["avgNum"]
    for key, value in HK.items():
        binnedHK[key] = np.zeros(
            len(secsOut), dtype="float"
        )  # [i] = np.nanmean(HK[key][indices],0)
    binnedSC = np.zeros((len(secsOut), dims[1]), dtype="float")

    for key in keysToSum:
        if key not in binnedHK.keys():
            keysToSum.remove(key)

    """
	try:
		plotDivisions = int(self.plotDivisions.text())
	except:
		plotDivisions = 100
		self.plotDivisions.setText("100")
	if plotDivisions > obs:
		plotDivisions = obs
		self.plotDivisions.setText(str(round(obs)))
	"""

    for i in range(len(secsOut)):  # nsteps):
        # if i % int(np.floor(obs/plotDivisions)) == 0:# or intvmr[i]>100:
        # 	self.progress.setValue(i+1)
        # self.processEvents()
        try:
            # indices = np.digitize(seconds, histval[i])
            indices = np.where(SCindices == i + 1)[0]
            # indices = np.where(np.logical_and(histval[i] <= seconds, histval[i+1] >= seconds))[0]
            binnedSC[i, :] = np.nanmean(SC["scans"][indices, :], 0)
        except:
            binnedSC[i, :] = np.nan  # math.nan
        try:
            indices = np.where(HKindices == i + 1)[0]
            for key, value in binnedHK.items():
                if key not in keysToSum:
                    binnedHK[key][i] = np.nanmean(HK[key][indices], 0)
                else:
                    binnedHK[key][i] = np.nansum(HK[key][indices], 0)
        except:
            for key, value in binnedHK.items():
                binnedHK[key][i] = np.nan
        """
		if hist[i] == 0: scanint[i,:] = math.nan
		# elif hist[i] == 1: scanint[i,:] = histval[i]
		else:
			indices = np.where(np.logical_and(histval[i] <= seconds, histval[i+1] >= seconds))[0]
			# scanint[i,:] = np.mean(SC['scans'][

			# IF CODE BREAKS USE THE FOLLOWING
			# indices = np.where(tmparray == histval[i])
			scanint[i,:] = np.mean(SC['scans'][indices,:],0)
			# if histmask[i]: scanint[i,:] = SC['scans'][mask[i]]
			# if histmask[i]:	scanint[i,:] = np.mean(SC['scans'][mask[i]:mask[i]+hist[i]],0)

			# if round(i*100/nsteps) == i/np.floor(nsteps/100):
		"""
        # try:
        # 	self.progress.setValue(i+1)
        # 	#app.processEvents()
        # 	self.processEvents()
        # except: pass
    # self.processEvents()

    for key, value in binnedHK.items():
        binnedHK[key] = binnedHK[key][: len(secsOut)]

    HK = copy.deepcopy(binnedHK)
    runningSC = copy.deepcopy(binnedSC)  # .copy()#scanint

    # self.progress.setValue(0)

    for i in range(len(secsOut)):  # nsteps):
        """
		if i % int(np.floor(obs/plotDivisions)) == 0:# or intvmr[i]>100:
			self.progress.setValue(i+1)
		self.processEvents()
		"""
        if i < runAvgSize:
            runningSC[i, :] = np.nanmean(binnedSC[0 : 2 * i + 1, :], 0)
        elif (len(secsOut) - i - 1) < runAvgSize:
            runningSC[i, :] = np.nanmean(binnedSC[2 * i - len(secsOut) - 1 :, :], 0)
        else:
            runningSC[i, :] = np.nanmean(
                binnedSC[i - runAvgSize : i + runAvgSize + 1, :], 0
            )

        for key, value in binnedHK.items():
            # binnedHK[key] = binnedHK[key][:len(secsOut)]
            if i < runAvgSize:
                binnedHK[key][i] = np.nanmean(HK[key][0 : 2 * i + 1], 0)
            elif (len(secsOut) - i - 1) < runAvgSize:
                binnedHK[key][i] = np.nanmean(HK[key][2 * i - len(secsOut) - 1 :], 0)
            else:
                binnedHK[key][i] = np.nanmean(
                    HK[key][i - runAvgSize : i + runAvgSize + 1], 0
                )
        # try:
        # 	self.progress.setValue(i+1)
        # 	self.processEvents()
        # except: pass

    # binnedSC = runningSC
    HK = binnedHK

    # NOW for the interpolation scheme to eliminate nans
    # Iterate through the 2048 points for pointwise interpolation of scans

    
    for i in range(len(runningSC[0, :])):
        nans, x = np.isnan(runningSC[:, i]), lambda z: z.nonzero()[0]
        runningSC[nans, i] = np.interp(x(nans), x(~nans), runningSC[~nans, i])
    for key, value in binnedHK.items():
        nans, x = np.isnan(HK[key]), lambda z: z.nonzero()[0]
        HK[key][nans] = np.interp(x(nans), x(~nans), HK[key][~nans])

    # Not sure if necessary anymore
    missing = [i for i, val in enumerate(runningSC[:, 0]) if not np.isfinite(val)]

    if len(missing) > 0:
        HK["PD"][missing] = -9999
        HK["tdetect"][missing] = -9999
        HK["tlaser"][missing] = -9999
        HK["temp1"][missing] = -9999
        HK["tbody"][missing] = -9999
        HK["temp2"][missing] = -9999
        HK["press"][missing] = -9999
        HK["current"][missing] = -9999
        HK["vlaser"][missing] = -9999
        HK["MFC"][missing] = -9999

    SC["juldate"] = np.array(juldate)
    SC["scans"] = runningSC  # scanint

    HK["juldate"] = np.array(juldate)

    # Section is only used for GUI update
    secsOut = (
        np.round(np.arange(start - 0.5 / Hz, stop + 0.5 / Hz, 1 / Hz), precision)
        + 0.5 / Hz
    )
    juldate = secsOut / (3600 * 24) + 0.5 + float(math.floor(SC["juldate"][0]))

    startText = time.strftime(
        "%Y%m%d_%H%M%S",
        time.gmtime(
            (juldate[0] - gcal2jd(1970, 1, 1)[0] - gcal2jd(1970, 1, 1)[1]) * 60 * 60 * 24
        ),
    )
    endText = time.strftime(
        "%Y%m%d_%H%M%S",
        time.gmtime(
            (juldate[-1] - gcal2jd(1970, 1, 1)[0] - gcal2jd(1970, 1, 1)[1]) * 60 * 60 * 24
        ),
    )

    return [HK, SC], startText, endText
