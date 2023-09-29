from common.libraryImports import *

from common.fileProcessing import *
from common.spectralModule import *

from clh2ui import *
import traceback

#import sys
sys.setrecursionlimit(2500)
# NOTES

# Appears to be an issue when creating large merge files and then trying to
# 	average them (causes segmentation fault)

# There appears to be a single point offset in time between older voigt processing
# 	and this new python code. (i.e. old codes time 6 equal to new codes time 5)

# Need to implement refined guessing routine such that it always uses the previous
# 	successful fits for next guess UNLESS there is chunk of time missing
# 	OR there appears to be some sort of divergent fit

# Need to implement some sort of narrowing function for allowing higher precision
# 	fits of the smaller absorption features (set mins and maxes as well)

# Implement better initial guessing routine (i.e. average all scans OR
# 	find well behaved signal to fit to prevent error prone initialization


class NCPopupWindow(QDialog):
    def __init__(self):
        QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        tmpobject = QLabel(self)
        #tmpobject.setGeometry(QRect(100, 20, 200, 50))
        tmpobject.setText("Select Water Vapor for Subtraction")

        self.ncMenu = QComboBox(self)  # self.cw)
        #self.ncMenu.setGeometry(QRect(100, 70, 200, 50))
        # 	#self.ncMenu.setStyleSheet("QComboBox { combobox-popup: 0; }");
        # self.ncMenu.addItems()
        self.ncMenu.setMaxVisibleItems(15)
        

    # def quit(self):
    # 	self.close()
    # def __init__(self):
    # 	QWidget.__init__(self)
    # def paintEvent(self, e):
    # self.cw = QWidget(self)
    # self.setCentralWidget(self.cw)

    # self.ncMenu = QComboBox()#self.cw)
    # self.ncMenu.setGeometry(QRect(0,0,100,100))
    # self.ncMenu.setStyleSheet("QComboBox { combobox-popup: 0; }");
    # self.ncMenu.addItems(np.array(['hi','bye']))
    # self.ncMenu.setMaxVisibleItems(15)
    # self.ncMenu.currentIndexChanged.connect(self.updateInterval)
    # self.ncMenu.setVisible(False)
    # def paintEvent(self, e):
    # 	dc = QPainter(self)
    # 	dc.drawLine(0,0,100,100)
    # 	dc.drawLine(100,0,0,100)


class Ui_MainWindow(QWidget):
    plotSignal = pyqtSignal(object)
    statusSignal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        #QGuiApplication().setAttribute(Qt.AA_DisableHighDpiScaling)
        self.title = "PyQt5 file dialogs"
        self.left = 20
        self.top = 50
        self.width = 960 * 1.8
        self.height = 540 * 1.7
        initUI(self)
        self.backOrder.setValue(2)
        #self.wvlgnthOrder.setValue(2)
        self.wvlngthOrder.setValue(2)
        self.threadpool = QThreadPool()
        
    def statusUpdate(self):
        print("signalupdate")

    def plotUpdate(self):
        print("plotupdate")

    def loadNC(self):
        # dataset = Dataset('C:/Users/rainw/Desktop/github/CLH2/python/SOCRATESrf02.nc')

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        defaultDir = os.path.expanduser("~").replace("\\", "/")
        # fileName, _ = QFileDialog.getOpenFileName(self, "Select NetCDF Files", defaultDir, "NetCDF Files (*.nc);;All Files (*)", options = options)
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select NetCDF Files",
            "./",
            "NetCDF Files (*.nc);;All Files (*)",
            options=options,
        )
        if fileName:
            dataset = Dataset(fileName)
        else:
            return

        msgBox = QMessageBox()  # .warning()
        msgBox.setText(
            "Would you like to load previously analyzed CLH-2 data or compute from NetCDF Parameters?"
        )
        msgBox.addButton(QPushButton("Post-processed"), QMessageBox.YesRole)
        msgBox.addButton(QPushButton("From NetCDF"), QMessageBox.NoRole)
        msgBox.addButton(QPushButton("Cancel"), QMessageBox.RejectRole)
        ret = msgBox.exec_()

        if ret == 0:  # msgBox == QMessageBox.Yes:
            try:
                fileName = self.VMRFileName
                # clhvmr = self.ints['VMR']
                # ret = 0
            except:
                fileName, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select processed CLH-2 data",
                    "./",
                    "Processed Files (*.txt;*.csv;*.ict);;All Files (*)",
                    options=options,
                )
            with open(fileName, "r") as csvFile:
                spamreader = csv.reader(csvFile, delimiter=",")
                fileData = []
                # headerOffset = 44
                for i, row in enumerate(spamreader):
                    tmprow = []
                    if i == 0:
                        headerSize = int(row[0])  # int(row.split(',')[0])
                        continue
                    if i == 6:
                        dateout = ", ".join(row)
                    if i < headerSize - 1:
                        continue
                    elif i == headerSize - 1:
                        header = row
                        continue
                    else:
                        badRowBool = 0
                        for item in row:
                            try:
                                (float(item))
                                tmprow.append(float(item))
                            except:
                                badRowBool = 1
                        if not badRowBool:
                            fileData.append(tmprow)

            fileData = np.array(fileData)
            # print(fileData[:,0]) #This lists all times
            fileTime = fileData[:, 0]
            # try: clhvmr = fileData[:,32]
            voigtIndex = 0
            for i, val in enumerate(header):
                if val.replace(" ", "") == "conc_1_1":  #'voigt0_ppmv':
                    voigtIndex = i
            try:
                clhvmr = fileData[:, voigtIndex]
            except:
                clhvmr = fileData[:, 12]
            press = fileData[:, 7]
            temp = (fileData[:, 6] + fileData[:, 4]) / 2.0
            MFC = fileData[:, 10]
            # clhvmr = fileData[:,33]*1.15
            # clhvmr = fileData[:,32]#*1.15 #Using new output files
        elif ret == 1:  # msgBox == QMessageBox.No:
            clhvmr = dataset.variables["VMR_CLH"][:]
            press = dataset.variables["PRESS_CLH"][:]
            temp = dataset.variables["TEMP_CLH"][:]
            MFC = np.ones(len(clhvmr)) * 3.5
            # MFC[:] = 3.5
        else:
            return

        try:
            clhvmrerr = fileData[:, voigtIndex + 1]
            # if clhvmrerr[i]/clhvmr[i]*100 > 20 or clhvmrerr[i] == 0 or clhvmrerr[i] < 9000:
            # 	clhvmr[i] = -9999
        except:
            pass

        dataStruct = {}
        dataStructDesc = {}
        dataStructUnits = {}

        CLHKeys = ["VMR_CLH", "press", "temp", "MFC"]

        dataStruct["VMR_CLH"] = clhvmr
        dataStruct["press"] = press
        dataStruct["temp"] = temp
        dataStruct["MFC"] = MFC

        """
		###########################################################
		########### August 2017 Calibration correction ############
		coefb = -0.786468748213585
		coefc = 1.089409599387933
		coefd = -0.000052670151220

		dataStruct['VMR_CLH'] = coefb * dataStruct['press'] + \
			coefc * dataStruct['VMR_CLH'] + \
			coefd * dataStruct['VMR_CLH'] * dataStruct['press']
		###########################################################

		###########################################################
		########### August 2017 Calibration correction ############
		coefa = -49.490827876592000
		coefb = -0.722823682040270
		coefc = 1.090510959601932
		coefd = -0.000054164941737

		dataStruct['VMR_CLH'] = coefa + coefb * dataStruct['press'] + \
			coefc * dataStruct['VMR_CLH'] + \
			coefd * dataStruct['VMR_CLH'] * dataStruct['press']
		###########################################################
        
		"""
        ####### June 6th Calibration Correction ########
        a = 1.05#0.95
        b = 1.015
        c = -0.025
        #### of the form y = a*VMR^b*press^c
        dataStruct['VMR_CLH'] = a*np.power(dataStruct['VMR_CLH'],b)*np.power(dataStruct['press'],c)
        
        ####### MFC CORRECTION FOR SOCRATES ######
        dataStruct['MFC'] *= 1.8



        dataStructDesc["VMR_CLH"] = "Cell volume mixing ratio"
        dataStructDesc["press"] = "Cell Pressure"
        dataStructDesc["temp"] = "Cell Temperature"
        dataStructDesc["MFC"] = "Mass flow controller reading"

        dataStructUnits["VMR_CLH"] = "ppmv"
        dataStructUnits["press"] = "mbar"
        dataStructUnits["temp"] = "C"
        dataStructUnits["MFC"] = "SLPM"

        # extraParams = []
        keysToRemove = []

        # extraParamKeys = ['TASX','ATX','PSX','CVCWC','CVCWCC','PLWCC','PLWCD_RWIO','PLWCPIP_RWII','DP_DPL','DP_VXL','DP_DPR']
        extraParamKeys = np.array(
            [
                ["TASX", "Total Airspeed", "m/s"],
                ["ATX", "Ambient Air Temperature", "C"],
                ["PSX", "Ambient Pressure", "mbar"],
                ["CVCWC", "CVI CWC", "(g/m^3)"],
                ["CVCWCC", "CVI Corrected CWC", "(g/m^3)"],
                ["PLWCC", "Unknown", "Unit"],
                ["PLWCD_RWIO", "Unknown", "Unit"],
                ["CONCD_RWIO", "Unknown", "Unit"],
                ["PLWCPIP_RWII", "Unknown", "Unit"],
                ["DP_DPL", "Dew Point Left", "C"],
                ["DP_VXL", "Dew Point VCSEL", "C"],
                ["DP_DPR", "Dew Point Right", "C"],
                ["VMR_VXL", "VCSEL mixing ratio", "ppmv"],
            ]
        )

        for key in extraParamKeys:
            print(key)
            try:
                dataStruct[key[0]] = dataset.variables[key[0]][:]
                dataStructDesc[key[0]] = key[1]
                dataStructUnits[key[0]] = key[2]
                # extraParams.append(dataset.variables[key][:])
            except:
                # input(key)
                keysToRemove.append(key[0])
                # extraParamKeys.remove(key)
                # print(extraParamKeys)
                # pass

        for key in dataStruct:
            dataStruct[key] = np.array(dataStruct[key])

        # for key in keysToRemove:
        # 	try:
        # 		del dataStruct[key]
        # 		del dataStructUnits[key]
        # 		del datastructDesc[key]

        # 	extraParamKeys.remove(key)
        # extraParams = np.array(extraParams)

        # MFC[:] = -0.0226*MFC[:]**3 + 0.014*MFC[:]**2 + 2.021*MFC[:]
        # MFC[:] = 1.722*MFC[:] + 0.014
        # dataStruct['MFC'] = 1.722*dataStruct['MFC'] + 0.014

        # PSX = dataset.variables['PSX'][:] #Static pressure (Maybe used corrected PSXC
        # ATX = dataset.variables['ATX'][:] #Ambient Temperature
        # TASX = dataset.variables['TASX'][:] #Airspeed

        # print(dataset.variables)
        # dataset = Dataset(self.openFileNamesDialog())
        # self.files = self.openFileNamesDialog()
        # self.w = NCPopupWindow()
        # self.w.setGeometry(QRect(100, 100, 600, 400))
        # self.w.show()

        try:
            timestamp = dataset.variables["time"]
        except:
            try:
                timestamp = dataset.variables["Time"]
            except:
                # Add error message to indicator
                return

        try:
            fileTime[0]
        except:
            fileTime = timestamp[:]

        # item, contupdate = QInputDialog.getItem(MainWindow, "QInputDialog.getItem()","Season:", list(dataset.variables.keys()),0, False)
        # item, proceed = QInputDialog.getItem(MainWindow, "NetCDF File","Select Vapor VMR for subtraction:", list(dataset.variables.keys()),0, False)
        # if not proceed: return

        # vmr = dataset.variables[item][:]
        # vmr = dataset.variables['VMR_VXL'][:]

        timestamp = np.array([np.round(x) for x in timestamp], dtype="int")
        fileTime = np.array([np.round(x) for x in fileTime], dtype="int")

        print(timestamp, fileTime)

        if max(fileTime) < 86400 and any(timestamp > 86400):
            fileTime[:] += 86400
        if max(timestamp) < 86400 and any(fileTime > 86400):
            timestamp[:] += 86400

        for i in range(2):
            # print(timestamp[0], fileTime[0], timestamp[-1], fileTime[-1], len(timestamp),len(fileTime))
            # print(min(timestamp),max(timestamp),min(fileTime),max(fileTime))
            startDiff = timestamp[0] - fileTime[0]
            if i == 1:
                startDiff *= -1
            if startDiff < 0:  # timestamp[0] < fileTime[0]:
                for key, value in dataStruct.items():
                    if key not in CLHKeys:
                        dataStruct[key] = dataStruct[key][np.abs(startDiff) :]
                # vmr = vmr[np.abs(startDiff):]
                timestamp = timestamp[np.abs(startDiff) :]
                # TASX = TASX[np.abs(startDiff):]
                # PSX = PSX[np.abs(startDiff):]
                # ATX = ATX[np.abs(startDiff):]
                # extraParams = extraParams[:,np.abs(startDiff):]
                if ret == 1:
                    press = press[np.abs(startDiff) :]
            else:
                for key, value in dataStruct.items():
                    if key in CLHKeys:
                        dataStruct[key] = dataStruct[key][np.abs(startDiff) :]
                # clhvmr = clhvmr[np.abs(startDiff):]
                # press = press[np.abs(startDiff):]
                # temp = temp[np.abs(startDiff):]
                # MFC = MFC[np.abs(startDiff):]
                # try: MFC = MFC[np.abs(startDiff):]
                # except: pass
                fileTime = fileTime[np.abs(startDiff) :]
                # if ret == 0: press = press[np.abs(startDiff):]
                # press = press[np.abs(startDiff):]

            for key, value in dataStruct.items():
                dataStruct[key] = np.flip(dataStruct[key], 0)
            # vmr = np.flip(vmr,0)
            # clhvmr = np.flip(clhvmr,0)
            # TASX = np.flip(TASX,0)
            # PSX = np.flip(PSX,0)
            # ATX = np.flip(ATX,0)
            # extraParams = np.flip(extraParams,1)
            # MFC = np.flip(MFC,0)
            # press = np.flip(press, 0)
            # temp = np.flip(temp, 0)

            timestamp = np.flip(timestamp, 0)
            fileTime = np.flip(fileTime, 0)

        # print(dataStruct)

        # flag = np.zeros(len(TASX))
        # testDom = np.arange(len(TASX))

        flag = np.zeros(len(dataStruct["TASX"]))
        testDom = np.zeros(len(dataStruct["TASX"]))

        # print(extraParamKeys, extraParams.shape)
        # print(np.where(np.array(extraParamKeys) == 'DP_DPL'))
        # print(np.where(np.array(extraParamKeys) == 'DP_DPR'))
        # print(np.where(np.array(extraParamKeys) == 'DP_VXL'))

        # testDPL = np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_DPL')[0][0],:])#dataset.variables['DP_DPL'][:] #Airspeed
        # testDPR = np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_DPR')[0][0],:])#dataset.variables['DP_DPR'][:] #Airspeed
        # testVXL = np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_VXL')[0][0],:])#dataset.variables['DP_VXL'][:] #Airspeed

        testDPL = copy.deepcopy(
            dataStruct["DP_DPL"]
        )  # np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_DPL')[0][0],:])#dataset.variables['DP_DPL'][:] #Airspeed
        testDPR = copy.deepcopy(
            dataStruct["DP_DPR"]
        )  # np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_DPR')[0][0],:])#dataset.variables['DP_DPR'][:] #Airspeed
        testVXL = copy.deepcopy(
            dataStruct["DP_VXL"]
        )  # np.array(extraParams[np.where(np.array(extraParamKeys) == 'DP_VXL')[0][0],:])#dataset.variables['DP_VXL'][:] #Airspeed

        maskedVXL = np.where(np.logical_or(np.ma.is_masked(testVXL), testVXL < -100))[0]
        flag[maskedVXL] = 1
        # cutoffValues = np.where(np.logical_and(validclhvmr > validvmr*res.x[1] + res.x[0] + 100, validclhvmr > validvmr))
        # print(maskedVXL)

        # Dew point to VMR (over water)
        A = 6.116441
        m = 7.591386
        Tn = 240.7263
        partialPressDPL = A * 10 ** (m * testDPL / (testDPL + Tn))
        partialPressDPR = A * 10 ** (m * testDPR / (testDPR + Tn))
        # Dew point to VMR (over ice)
        A = 6.114742
        m = 9.778707
        Tn = 273.1466
        iceIndicesDPL = np.where(testDPL <= 0)
        partialPressDPL[iceIndicesDPL] = A * 10 ** (
            m * testDPL[iceIndicesDPL] / (testDPL[iceIndicesDPL] + Tn)
        )
        # DPL_VMR = 10**6*(partialPressDPL/(PSX-partialPressDPL))
        DPL_VMR = 10 ** 6 * (partialPressDPL / (dataStruct["PSX"] - partialPressDPL))

        iceIndicesDPR = np.where(testDPR <= 0)
        partialPressDPL[iceIndicesDPR] = A * 10 ** (
            m * testDPR[iceIndicesDPR] / (testDPL[iceIndicesDPR] + Tn)
        )
        # DPR_VMR = 10**6*(partialPressDPR/(PSX-partialPressDPR))
        DPR_VMR = 10 ** 6 * (partialPressDPR / (dataStruct["PSX"] - partialPressDPR))

        for i in range(len(DPR_VMR) - 1):
            if (
                DPR_VMR[i + 1] < 0
                or np.ma.is_masked(DPR_VMR[i + 1])
                or np.isnan(DPL_VMR[i + 1])
            ):
                DPR_VMR[i + 1] = DPR_VMR[i]
                if flag[i + 1] == 1:
                    flag[i + 1] += 1
            if (
                DPL_VMR[i + 1] < 0
                or np.ma.is_masked(DPL_VMR[i + 1])
                or np.isnan(DPL_VMR[i + 1])
            ):
                DPL_VMR[i + 1] = DPL_VMR[i]

        # print(len(testVXL),len(maskedVXL))
        testVXL[maskedVXL] = testDPR[maskedVXL]

        # testDPL = np.ma.masked_where(testDPL < -100, testDPL)
        # testDPL = np.ma.masked_where(np.isnan(testDPL), testDPL)
        # for i in range(len(testDom)):
        # 	if np.ma.is_masked(testDPL[i]) or testDPL[i] < -100:# or np.ma.is_masked(clhvmr[i]) or np.ma.is_masked(PSX[i]) or np.ma.is_masked(ATX[i]):
        # 		testDPL[i] = np.nan
        # b,a = butter(5, 2*0.007/(1), btype = 'low', analog = False)
        b, a = butter(2, [0.01, 0.99], btype="bandstop", analog=False)
        # b,a = butter(5, 0.015, btype = 'low', analog = False)
        #'wn' is in half-cycles/sample
        # in other words to low pass anything lower than 0.1Hz (10 seconds) on a 1Hz data rate of 1000 samples.
        # would be computed using (cutoff frequency)/(datafrequency/2) so 0.1 hz cutoff would be 0.1/(2)
        DPR_VMR = np.ma.masked_invalid(np.array(DPR_VMR))
        for i in range(1):
            DPR_VMR = filtfilt(b, a, DPR_VMR)

        dataStruct["VMR_VXL"][maskedVXL] = DPR_VMR[maskedVXL]

        # vmr[maskedVXL] = DPR_VMR[maskedVXL]
        vmr = copy.deepcopy(dataStruct["VMR_VXL"])
        clhvmr = copy.deepcopy(dataStruct["VMR_CLH"])

        self.figure.clear()
        # nullSpectra = zeros(len(x[lower1:upper2]),dtype='float')
        ax = self.figure.add_subplot(111)
        # line1, line2, = ax.plot(fileTime,validclhvmr,'k',fileTime,validvmr*res.x[1] + res.x[0],'r')#timestamp,vmr,'r')
        # line1, line2, line3, = ax.plot(testDom,testVXL,'b',testDom,testDPR,'k',testDom,testDPL,'r')#timestamp,vmr,'r')
        line1, line2, line3, = ax.plot(
            testDom, vmr, "b", testDom, DPL_VMR, "k", testDom, DPR_VMR, "r"
        )  # timestamp,vmr,'r')
        # plt.plot(testDom,testVXL,'k',testDom,testDP1,'r')#timestamp,vmr,'r')
        # plt.show()
        ax.relim()
        ax.autoscale()

        self.canvas.draw()
        # app.processEvents()
        self.processEvents()
        # return
        # input('wait')

        # endDiff = timestamp[-1] - fileTime[-1]

        # if timestamp[-1] < fileTime[-1]:
        # 	clhvmr = clhvmr[:-np.abs(endDiff)]
        # 	#MFC = MFC[:-np.abs(endDiff)]
        # 	fileTime = fileTime[:-np.abs(endDiff)]
        # else:
        # 	vmr = vmr[:-np.abs(endDiff)]
        # 	timestamp = timestamp[:-np.abs(endDiff)]

        # clhvmr = list(clhvmr)
        # clhvmr = (dataset.variables['VMR_CLH'][:])
        # validclhvmr[np.isnan(clhvmr)] = 0
        # validclhvmr = np.array(clhvmr[:])
        # validvmr = np.array(vmr[:])

        validclhvmr = np.array(clhvmr[:])
        validvmr = np.array(vmr[:])

        for i in range(len(vmr)):
            if (
                np.ma.is_masked(vmr[i])
                or np.ma.is_masked(clhvmr[i])
                or np.ma.is_masked(dataStruct["PSX"][i])
                or np.ma.is_masked(dataStruct["ATX"][i])
            ):
                # if np.ma.is_masked(vmr[i]) or np.ma.is_masked(clhvmr[i]) or np.ma.is_masked(PSX[i]) or np.ma.is_masked(ATX[i]):
                validvmr[i] = np.nan
                validclhvmr[i] = np.nan

        # validvmr[np.isnan(vmr)] = 0

        # try:
        # 	validclhvmr[np.where(MFC < 1.0)[0]] = np.nan
        # 	validvmr[np.where(MFC < 1.0)[0]] = np.nan
        # except: pass
        # if len(validvmr) < len(validclhvmr):
        # 	validvmr = np.r_[validvmr,np.zeros(len(validclhvmr)-len(validvmr))]
        # else:
        # 	validvmr = validvmr[:len(validclhvmr)]

        # ADD Condition for valid only when flow rates are high enough

        # print(len(validclhvmr),len(validvmr))

        result = np.correlate(validvmr, validclhvmr, mode="same")
        fullresult = np.correlate(validclhvmr, validvmr, "full")
        fullresult = np.roll(fullresult, len(validvmr))[0 : len(validvmr)]
        lag = np.argmax(fullresult)
        # maxindex = np.argmax(np.correlate(np.roll(vmr,0),np.roll(clhvmr,0),'full'))
        # clhvmr = np.roll(clhvmr,10) #Rolls the data backwards
        # maxindex = np.argmax(np.correlate(validclhvmr,validvmr,'full'))
        # maxindex - len(array) is the amount to shift first value (negative backwards)
        # To perform a negative roll (roll backwards), np.roll(array,+#)
        # offset = len(validvmr)
        # print(lag)

        fun = lambda x: np.sum(
            np.abs(
                np.ma.masked_invalid(validclhvmr)
                - np.ma.masked_invalid(validvmr) * x[1]
                - x[0]
            )
        )
        # res = scimin(fun,np.array([1.0,0.0]))
        res = scimin(fun, np.array([1.0, 0.0]))

        # validvmr = validvmr*res.x[1] - res.x[0]
        # cutoffValues = np.where(validclhvmr > validvmr*res.x[1] + res.x[0] + 500)[0]
        # cutoffValues = np.where(np.logical_and(validclhvmr > validvmr*res.x[1] + res.x[0] + 100, validclhvmr > validvmr))
        # validclhvmr[cutoffValues] = np.nan
        # validvmr[cutoffValues] = np.nan

        fun = lambda x: np.sum(
            np.abs(
                np.ma.masked_invalid(validclhvmr)
                - np.ma.masked_invalid(validvmr) * x[1]
                - x[0]
            )
        )
        res = scimin(fun, np.array([1.0, 0.0]))
        res.x[1] = 1.00
        res.x[0] = 0.00

        # print(res)

        # CVMR = validclhvmr - validvmr*res.x[1] - res.x[0]
        CVMR = clhvmr - vmr * res.x[1] - res.x[0]
        # enhFac = np.pi*100*TASX*(0.2375)**2/(MFC*(1000.0/60.0)*(1013.25/press)*(313.15/298.15))
        # print(len(TASX),len(MFC),len(press))
        # enhFac = np.pi*100.0*TASX*(0.2375)**2/(MFC*(1000.0/60.0)*(1013.25/press)*(313.15/298.15))
        enhFac = (
            np.pi
            * 100.0
            * dataStruct["TASX"]
            * (0.2375) ** 2
            / (
                dataStruct["MFC"]
                * (1000.0 / 60.0)
                * (1013.25 / dataStruct["press"])
                * (313.15 / 298.15)
            )
        )
        CWC = CVMR / enhFac
        CWCgperkg = (CWC / 1000000.0) * (18.01 / 0.0289)
        # ambPress = press[:]
        # CWCkgperm3 = (7.25*PSX*0.0289)/((273.15+ATX)*0.602)
        # CWCkgperm3 = (7.25*press*0.0289)/((273.15+temp)*0.602)
        CWCkgperm3 = (7.25 * dataStruct["press"] * 0.0289) / ((273.15 + 40) * 0.602)
        CWCgperm3 = CWCgperkg * CWCkgperm3

        cviFile, _ = QFileDialog.getOpenFileName(
            self,
            "Select processed CVI data",
            "./",
            "Processed Files (*.xlsx;*.csv;*.ict);;All Files (*)",
            options=options,
        )

        # Section for diagnostics with finalized CVI data
        # File with better CWC's
        cviTime = []
        cviLow = []
        cviHigh = []
        with open(cviFile, "r") as csvFile:
            spamreader = csv.reader(csvFile, delimiter=",")
            # print(spamreader[0,:])
            # for i, row in enumerate(spamreader):
            for row in spamreader:
                try:
                    cviTime.append(int(np.floor(float(row[0]))))
                    cviLow.append(float(row[14]))
                    cviHigh.append(float(row[15]))
                except:
                    pass

        cviTime = np.array(cviTime)

        startDiff = min(fileTime) - min(cviTime)
        spanDiff = int((max(fileTime) - min(fileTime)) - (max(cviTime) - min(cviTime)))

        cviTime -= int(2)
        # cviTime += int((startDiff + spanDiff/2.0))

        adjCVILow = np.zeros(len(fileTime), dtype="float")
        adjCVIHigh = np.zeros(len(fileTime), dtype="float")

        for i, time in enumerate(fileTime):
            matchIndex = np.where(time == cviTime)[0]
            if len(matchIndex) == 0:
                adjCVILow[i] = -9999
                adjCVIHigh[i] = -9999
                continue
            elif len(matchIndex) >= 1:
                matchIndex = matchIndex[0]
            adjCVILow[i] = cviLow[matchIndex]
            adjCVILow[i] = cviHigh[matchIndex]

        # Read in different
        # result = np.correlate(validvmr,validclhvmr, mode = 'same')
        # fullresult = np.correlate(newCVI, dataStruct['CVCWCC'], 'full')
        # fullresult = np.roll(fullresult,len(fileTime))[0:len(fileTime)]
        # lag = np.argmax(fullresult)
        # fullresult = np.roll(newCVI,lag)
        # CVICWC = copy.deepcopy(fullresult)

        # Calculation of required MFC to match CVI
        # Take CWC of CVI divide
        dMFCLow = copy.deepcopy(adjCVILow)  # dataStruct['CVCWCC'])
        dMFCHigh = copy.deepcopy(adjCVIHigh)  # dataStruct['CVCWCC'])

        noMFCeFac = enhFac * dataStruct["MFC"]

        dMFCLow /= CWCkgperm3 * CWCgperkg * enhFac
        dMFCHigh /= CWCkgperm3 * CWCgperkg * enhFac

        dMFCLow *= noMFCeFac
        dMFCHigh *= noMFCeFac

        # CVICWC /= CWCkgperm3
        # CVICWC /= (CWCgperkg*enhFac)
        # CVICWC *= noMFCeFac

        # mask = np.where(adjCVIHigh < 0.05)[0]
        mask = np.where(adjCVIHigh < 0.1)[0]
        dMFCLow[mask] = -9999
        dMFCHigh[mask] = -9999

        for i in range(len(vmr)):
            if (
                np.ma.is_masked(vmr[i])
                or np.ma.is_masked(clhvmr[i])
                or np.ma.is_masked(dataStruct["PSX"][i])
                or np.ma.is_masked(dataStruct["ATX"][i])
                or np.isnan(clhvmr[i])
            ):
                # if np.ma.is_masked(vmr[i]) or np.ma.is_masked(clhvmr[i]) or np.ma.is_masked(PSX[i]) or np.ma.is_masked(ATX[i]) or np.isnan(clhvmr[i]):
                vmr[i] = -9999  # np.nan
                clhvmr[i] = -9999  # np.nan
                CWC[i] = -9999
                CWCgperkg[i] = -9999
                CWCkgperm3[i] = -9999
                CWCgperm3[i] = -9999

        dataStruct["VMR_CLH"] = clhvmr
        dataStruct["VMR_VXL"] = vmr

        dataStruct["CVMR"] = CVMR
        dataStructDesc["CVMR"] = "Mixing ratio of condensed phase water"
        dataStructUnits["CVMR"] = "ppmv"

        dataStruct["eFact"] = enhFac
        dataStructDesc["eFact"] = "Enhancement Factor"
        dataStructUnits["eFact"] = "Unitless"

        dataStruct["CWCppmv"] = CWC
        dataStructDesc["CWCppmv"] = "Mixing ratio of condensed phase water"
        dataStructUnits["CWCppmv"] = "ppmv"

        dataStruct["CWCgperkg"] = CWCgperkg
        dataStructDesc["CWCgperkg"] = "Condensed water content"
        dataStructUnits["CWCgperkg"] = "g/kg"

        dataStruct["CWCkgperm3"] = CWCkgperm3
        dataStructDesc["CWCkgperm3"] = "Condensed water content"
        dataStructUnits["CWCkgperm3"] = "kg/m^3"

        dataStruct["CWC"] = CWCgperm3
        dataStructDesc["CWC"] = "Condensed water content"
        dataStructUnits["CWC"] = "g/m^3"

        dataStruct["calCVI_high"] = adjCVIHigh
        dataStructDesc["calCVI_high"] = "Calibrated CVI CWCs High"
        dataStructUnits["calCVI_high"] = "g/m^3"

        dataStruct["calCVI_low"] = adjCVILow
        dataStructDesc["calCVI_low"] = "Calibrated CVI CWCs Low"
        dataStructUnits["calCVI_low"] = "g/m^3"

        dataStruct["dMFC_high"] = dMFCHigh
        dataStructDesc[
            "dMFC_high"
        ] = "Derived MFC necessary for CVI (high) to match CLH2 CWCs"
        dataStructUnits["dMFC_high"] = "SLPM"

        dataStruct["dMFC_low"] = dMFCLow
        dataStructDesc[
            "dMFC_low"
        ] = "Derived MFC necessary for CVI (low) to match CLH2 CWCs"
        dataStructUnits["dMFC_low"] = "SLPM"

        # maxindex = np.argmax(np.correlate(clhvmr,np.roll(vmr,lag),'full'))
        # print(maxindex-len(vmr))

        # This function should ROLL the vcsel data time onto the clh2 time
        # vmr = validvmr
        # vmr = np.roll(vmr,lag)
        # timestamp = fileTime

        # print(len(result))
        # print(len(vmr))

        self.figure.clear()
        # nullSpectra = zeros(len(x[lower1:upper2]),dtype='float')
        ax = self.figure.add_subplot(111)
        # line1, line2, = ax.plot(fileTime,validclhvmr,'k',fileTime,validvmr*res.x[1] + res.x[0],'r')#timestamp,vmr,'r')
        # line1, line2, = ax.plot(fileTime,clhvmr,'k',fileTime,vmr*res.x[1] + res.x[0],'r')#timestamp,vmr,'r')
        line1, line2, = ax.plot(
            fileTime, dataStruct["CWC"], "k", fileTime, adjCVILow, "r"
        )  # timestamp,vmr,'r')
        # line1, line2, = ax.plot(fileTime,clhvmr,'k',fileTime,vmr*res.x[1] + res.x[0],'r')#timestamp,vmr,'r')
        # line1, = ax.plot(fileTime,validclhvmr-validvmr,'k')
        # line1, = ax.plot(fileTime,result,'k')
        # line1, = ax.plot(fileTime,CWC,'k')
        # outName = (''.join(fileName.split('packaged_')[:-1])+'packaged_'+str(timestamp)+'.txt')

        for key in dataStruct:
            dataStruct[key][np.where(dataStruct[key] < -999.0)[0]] = -9999

        # header = ['VMR Correction Coefficients']
        # header.append('Slope')
        # header.append("{:.3e}".format(res.x[1]))
        # header.append('Intercept')
        # header.append("{:.3e}".format(res.x[0]))

        packagedFileName = "./packagedHeader.txt"
        outName = fileName  # .replace('packaged','CWC')

        datestring = fileName.split("_")[2]
        # datestring = datestring.split('-')
        # if len(datestring) > 1: datestring = datestring[1]

        outName = self.namingConvention(outName, datestring, "Diagnostics")
        # print(self.namingCon

        variableNames = []
        variableDesc = []
        variableUnits = []
        for key, value in dataStruct.items():
            variableNames.append(key)
            variableDesc.append(dataStructDesc[key])
            variableUnits.append(dataStructUnits[key])

        outData = np.c_[fileTime]
        for key in dataStruct:
            outData = np.c_[outData, dataStruct[key]]

        self.saveFormat(
            dateout, outName, outData, variableNames, variableDesc, variableUnits
        )

        outName = self.namingConvention(outName, datestring)
        self.saveFormat(
            dateout,
            outName,
            np.c_[fileTime, dataStruct["CWC"]],
            ["CWC"],
            [dataStructDesc["CWC"]],
            [dataStructUnits["CWC"]],
        )

        """
		with open(outName, 'w', newline='') as outFile:
			with open(packagedFileName, 'r') as headerFile:
				for i, line in enumerate(headerFile):#line = parFile.readLine()
					#if i == 10:
					#	outFile.write('1,1,1,1,1\r\n')
					#elif i == 11:
					#	outFile.write('-9999,-9999,-9999\r\n')
					outFile.write(line)

			outFile.write('\r\n')
			#headerstring = 'UTC_Start, PD, Tdetect, Tlaser, Tcell, Tbody, Tcell2, Pcell, Claser, Vlaser, MFC, AbInt, VMR, Dark, IndexMax'
			headerstring = 'Seconds, CLHVMR, VXLVMR, flag, Pres, Temp, MFC, CWC, CWC (g/kg), CWC (kg/m^3), CWC (g/m^3)'
			for param in extraParamKeys:
				headerstring += ', '+param
			headerstring += '\r\n'
			outFile.write(headerstring)

			outData = np.c_[fileTime,clhvmr,vmr,flag,press,temp,MFC,CWC,CWCgperkg, CWCkgperm3, CWCgperm3, np.transpose(extraParams)]


			for row in outData:
				#tmp = '{:11d}'.format(int(row[0]))+','
				tmp = '{:.3f}'.format((row[0]))+','
				row = row[1:]
				#tmp+=','.join(["{:11.6f}".format(x) for x in row])
				tmp+=','.join(["{:.6e}".format(x) for x in row])
				tmp+='\r\n'
				outFile.write(tmp)
		"""

        # with open(outName,'w',newline='') as csvFile:
        # 	spamwriter = csv.writer(csvFile, delimiter = ',')
        # 	#spamwriter.writerow(header)
        # 	titles = ['Seconds','CLHVMR','VXLVMR','flag','Pres','Temp','MFC','CWC','CWC (g/kg)', 'CWC (kg/m^3)', 'CWC (g/m^3)']
        # 	titles.extend(extraParamKeys)
        # 	spamwriter.writerow(titles)
        # 	#spamwriter.writerow(['Seconds','CLHVMR','VXLVMR','CWC','CWC (g/kg)', 'CWC (kg/m^3)', 'CWC (g/m^3)'].extend)
        # 	#spamwriter.writerows(np.c_[fileTime,clhvmr,vmr,CWC,CWCgperkg, CWCkgperm3, CWCgperm3])
        # 	spamwriter.writerows(np.c_[fileTime,clhvmr,vmr,flag,press,temp,MFC,CWC,CWCgperkg, CWCkgperm3, CWCgperm3, np.transpose(extraParams)])

        ax.relim()
        ax.autoscale()

        self.canvas.draw()
        # app.processEvents()
        self.processEvents()

    def updateInterval(self):
        self.startTime.setText(self.timeList[self.timeMenu.currentIndex()][0])
        self.endTime.setText(self.timeList[self.timeMenu.currentIndex()][1])

    def selectFiles(self):
        self.files = self.openFileNamesDialog()
        self.loadFiles()

    def loadFiles(self, extract=False):

        self.pickleSave = False  # True
        if self.pickleSave:
            self.pickleDict = {}

        self.extractTimes = extract
        # self.files = self.openFileNamesDialog()
        # files = ['/mnt/c/Users/rainw/Desktop/JPL_July_Visit/JPL_CLiH_Data_Purge_7-21-17/CLH2-20170720_1648_HK_merged','/mnt/c/Users/rainw/Desktop/JPL_July_Visit/JPL_CLiH_Data_Purge_7-21-17/CLH2-20170720_1648_SC_merged']

        self.basepath = self.files[0]
        self.basepath = (
            "/".join(self.basepath.split("/")[:-1])
            + "/"
            + self.timeMenu.currentText().replace(",", "_").replace(" ", "")
            + ".dat"
        )
        app.processEvents()

        if self.files:
            if len(self.files) >= 2:
                self.files = mergefiles(self.files)
            elif len(self.files) < 2:
                return

            self.canvas.draw()

            saveCSV = self.extractData.isChecked()

            if ".csv" in self.files[0]:
                newFmt = True
                self.newFmt = True
            else:
                newFmt = False
                self.newFmt = False

            self.SC = readSC(self.files[1], newFmt, saveCSV)
            self.HK = readHK(self.files[0], newFmt, saveCSV)

            self.statusBar.setText("Loaded HK/SC files, beginning time shift corrections")

            self.HK[0]["juldate"] = fixjuldate(self.HK[0]["juldate"])
            self.SC[0]["juldate"] = fixjuldate(self.SC[0]["juldate"])

            self.statusBar.setText("Finished correcting time shifts, beginning averaging")

            for i in range(self.SC[0]["scans"].shape[0]):
                tmpmax = np.argmax(np.abs(self.SC[0]["scans"][i, :]))
                # Uncomment for scan alignment shifting
                # self.SC['scans'][i,:] = np.r_[self.SC['scans'][i,tmpmax:],self.SC['scans'][i,:tmpmax]];
                # self.SC['scans'][i,:] = np.r_[self.SC['scans'][i,:]];
            # plt.plot(SC['scans'][0,:])
            # plt.show()

            # np.save('/mnt/c/Users/rainw/Desktop/github/CLH2/python/sampleSpectra',SC['scans'][0,:])

            # self.numObservations.setText(str(round(len(self.SC['scans'][:,0]))))
            # self.averageData(HK, SC, Hz, runAvgBinSize)
            if self.newFmt:
                [self.HK[0], self.SC[0]], startText, endText = averageData(
                    self.HK[0], self.SC[0], 1.0, int(1)
                )  # 5.0)#5.0)#5.0)#1.0/5.0)#30.0)#1.0/60.0)#0.01)#5.0)#10.0)
            else:
                [self.HK[0], self.SC[0]], startText, endText = averageData(
                    self.HK[0], self.SC[0], 1, 1
                )  # 5.0)#5.0)#5.0)#1.0/5.0)#30.0)#1.0/60.0)#0.01)#5.0)#10.0)
             
            self.startTime.setText(startText)
            self.endTime.setText(endText)

            self.extractTimes = False

            self.statusBar.setText(
                "Files loaded and averaged, press 'Begin Analysis' for analysis and output"
            )

            self.beginAnalysisButton.setDisabled(False)

            # For normalizing the spectra to account for various coadds
            # dims = SC['scans'].shape
            # for i in range(dims[0]):
            # 	SC['scans'][i,:] = SC['scans'][i,:]/np.linalg.norm(SC['scans'][i,:])

    def extraction(self):
        numDark = 45  # 128#150#45
        fitlen = 100
        celltemp = np.nanmean(np.c_[self.HK[0]["temp1"], self.HK[0]["temp2"]], 1)

        saturatedVoltage = 3.95

        plotscans = 1
        figdir = 1
        ints = self.lineint(
            self.SC[0]["scans"],
            numDark,
            plotscans,
            fitlen,
            self.HK[0]["press"],
            celltemp,
            figdir,
            saturatedVoltage,
        )

        self.ints = ints

        if self.closeTrigger:
            return

        # for key, value in ints.items():
        # 	print(key)

        fitparams = -9999

        # datestring = ''.join(''.join(''.join(str(self.files[0]).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
        datestring = "".join(
            "".join("".join(str(self.files[0]).split("/")[-1:]).split("-")[-1:]).split(
                "_"
            )[0]
        )
        outName = (
            "/".join(self.files[0].split("/")[:-1])
            + "/"
            + "CLH2-"
            + datestring
            + "_packaged_.txt"
        )
        datestring = "".join(datestring.split("_")[0])

        # outNamePlot = '/'.join(self.files[0].split('/')[:-1])+'/'+'CLH2-'+datestring+'_plot_.png'
        outNamePlot = (
            "/".join(self.files[0].split("/")[:-1])
            + "/"
            + "CLH2-"
            + datestring
            + "_plot_.png"
        )

        # seconds = np.round((self.HK['juldate'] -
        # 	gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[0]-
        # 	gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[1])*86400)
        seconds = (
            self.HK[0]["juldate"]
            - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[0]
            - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[1]
        ) * 86400

        # self.seconds = seconds

        if self.performFits.isChecked():
            fitparams = self.linefits(
                ints[0],
                self.HK[0],
                self.SC[0]["scans"],
                numDark,
                self.backOrder.value(),
                self.numLines.value(),
                self.wvlngthOrder.value(),
            )

        self.outName = outName
        CLHtime = self.saveText(self.HK, ints, fitparams, outName)
        self.CLHtime = CLHtime

        self.plotResults(self.HK[0], self.SC[0], ints[0], outNamePlot)

        self.statusBar.setText(
            "Files analyzed and output file has been created. Please close the program"
        )

    def lineint(
        self, scans, numDark, plotscans, fitlen, press, celltemp, figdir, saturatedVoltage
    ):
        """Old processing module.

		Processing module

		inputs:
			scans: matrix containing scans
			numDark: Number of bits devoted to background measurement
			plotScans: bool to determine if scans are plotted
			fitlen: # of bits on either end of spectrum to use for background
			press: array of pressures
			cellTemp: array of cell temperatures
			figdir: directory where figures are saved to
			saturatedVoltage: Voltage threshold to use for signal saturation indicator
		"""

        dims = scans.shape
        obs = dims[0]
        scanpts = dims[1]

        x = np.arange(scanpts)
        # powerzero = np.mean(scans[:,2:numDark+1],1)
        powerzero = np.nanmean(scans[:, 2 : 45 - 5], 1)  # numDark+1],1)

        lower1 = numDark
        lower2 = numDark + fitlen
        upper1 = round(scanpts - fitlen * 0.75)
        upper2 = scanpts - 1

        intvmr = np.arange(float(obs))
        centerindex = np.arange(obs)
        vscan = np.arange(scanpts)

        ims = []
        self.figure.clear()

        nullSpectra = np.zeros(len(x[lower1:upper2]), dtype="float")
        ax = self.figure.add_subplot(111)

        # line1, line2, line3, line4, line5, line6, line7, = ax.plot(x[lower1:upper2],nullSpectra,'k',x[lower1:upper2],nullSpectra,'r',
        # 	x[lower1:upper2],nullSpectra,'b',x[lower1:upper2],nullSpectra,'y',
        # 	x[lower1:upper2],nullSpectra,'g',x[lower1:upper2],nullSpectra,'m',
        # 	x[lower1:upper2],nullSpectra,'c')
        line1, line2, line4 = ax.plot(
            x[lower1:upper2],
            nullSpectra,
            "k",
            x[lower1:upper2],
            nullSpectra,
            "r",
            x[lower1:upper2],
            nullSpectra,
            "y",
        )
        ax2 = ax.twinx()

        line3, = ax2.plot(x[lower1:upper2], nullSpectra, "b")

        self.progress.setRange(0, obs - 1)
        self.progress.setValue(0)

        try:
            plotDivisions = int(self.plotDivisions.text())
        except:
            plotDivisions = 100
            self.plotDivisions.setText("100")
        if plotDivisions > obs:
            plotDivisions = obs
            self.plotDivisions.setText(str(round(obs)))

        originalUpper2 = upper2
        originalUpper1 = upper1
        for i in range(obs):
            if self.closeTrigger:
                return
            upper2 = originalUpper2
            upper1 = originalUpper1

            while (
                np.abs(scans[i, upper2] > saturatedVoltage)
                and upper2 > upper1 + 10
                and np.abs(scans[i, upper2]) <= np.abs(scans[i, upper2 - 1])
            ):
                upper2 -= 1
            if scans[i, upper2] > saturatedVoltage:
                while np.abs(scans[i, upper2]) > saturatedVoltage and upper1 > 300:
                    upper1 -= 1
                    upper2 -= 1

            if self.newFmt:
                upper2 = originalUpper2
                upper1 = originalUpper1

            # if upper1 != originalUpper1:
            # 	print(upper1)

            # print(upper2)

            scanact = -np.abs((scans[i, :]) - powerzero[i])
            if self.newFmt:
                scanact = -np.abs(scans[i, :])
            yarr = np.r_[scanact[lower1 : lower2 + 1], scanact[upper1 : upper2 + 1]]
            xarr = np.r_[x[lower1 : lower2 + 1], x[upper1 : upper2 + 1]]
            fitout = np.polyfit(xarr, yarr, 3)
            # fitline = fitout[3] + fitout[2]*x + fitout[1]*x**2 + fitout[0]*x**3
            fitline = (
                fitout[3]
                + fitout[2] * x
                + fitout[1] * pow(x, 2.0)
                + fitout[0] * pow(x, 3.0)
            )
            scanfit = scanact - fitline
            # valid = [i for i, val in enumerate(x) if val > lower1]

            valid = np.where(x > lower1)
            # print(valid)

            maxindex = np.argmin(scanfit[valid])

            # maxindex+=lower1
            power = fitline[maxindex]
            powervo = scanact[maxindex]
            scanscale = scanact / fitline

            # Code for plotting various data
            centerindex[i] = maxindex + lower1 + 1

            try:
                intvmr[i] = np.trapz(1.0 - scanscale[valid], x=vscan[valid])
            except:
                intvmr[i] = -9999

            if i % int(np.floor(obs / plotDivisions)) == 0:  # or intvmr[i]>100:
                scaling = np.max(
                    np.r_[np.abs(scanact[lower1:upper2]), np.abs(fitline[lower1:upper2])]
                ) / max(1.0 - scanscale[lower1:upper2])

                # line1.set_ydata(self.spectralModel(out.params,x[left:-right]))
                line1.set_ydata(np.abs(scanact[lower1:upper2]))
                line1.set_xdata(x[lower1:upper2])
                ax.set_title("Raw Spectra")
                ax.set_xlabel("Bit #")
                ax.set_ylabel("Voltage (V)")

                line2.set_ydata(-fitline[lower1:upper2])
                line2.set_xdata(x[lower1:upper2])

                line4.set_ydata(
                    np.abs(scans[i, lower1:originalUpper2])
                )  # -scanact[lower1:upper2])
                line4.set_xdata(x[lower1:originalUpper2])

                # ax2 = ax.twinx()

                line3.set_ydata((1.0 - scanscale[lower1:upper2]))  # *scaling)
                line3.set_xdata(x[lower1:upper2])
                ax2.set_ylabel("Absorption")
                # line3.set_ydata(np.abs(scans[i,upper1:]))#*scaling)
                # line3.set_xdata(np.arange(len(scans[i,upper1:]))*512.0/len(scans[i,upper1:]))
                # ax2.set_ylabel('Absorption')

                # line4.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,0))

                # if numlines > 1: line5.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,1))

                ax.relim()
                ax.autoscale_view()
                ax2.relim()
                ax2.autoscale_view()

                # Uncomment for saving animation
                # ims.append([line1])
                # if numlines == 1: ims.append([line1,line2,line3,line4])

                # ax.draw_artist(ax.patch)
                # ax.draw_artist(line)
                # ax2.draw_artist(ax2.patch)
                # ax2.draw_artist()

                # self.canvas.update()
                # self.canvas.flush_events()

                self.canvas.draw()
                self.processEvents()

            self.progress.setValue(i)
            # time.sleep(1)

        powermax = (-1) * np.min(scans, 1)
        # print(powermax.shape)
        # March 2013 cal
        # fitted = np.array([-8.0605e3, -7.1624e0, -7.0584e3, -6.3956e0, -9.0851e-2, 1.0054e-1, 2.4235e-4])

        # October cal1
        # fitted = np.array([1.78e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])
        # October cal2
        # fitted = np.array([9e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])

        # Commented out prior to SOCRATES
        fitted = np.array(
            [
                9.9882e4,
                -6.3415e3,
                2.113e3,
                1.3178e1,
                -6.0409e-2,
                6.2395e-2,
                1.6877e-4,
                -1.04886e5,
            ]
        )

        VMR = (
            (
                fitted[0]
                + fitted[1] * press
                + fitted[2] * intvmr
                + fitted[3] * press * intvmr
            )
            / (1 + fitted[4] * press + fitted[5] * intvmr + fitted[6] * press * intvmr)
            + fitted[7]
        )
        # VMR = (fitted[0]+fitted[1]*press + fitted[2]*intvmr + fitted[3]*press*intvmr)/(1+fitted[4]*press + fitted[5]*intvmr + fitted[6]*press*intvmr)

        # powerzero = np.mean(scans[:,4:35],1)
        # print(powerzero.shape)

        ints = {
            "dark": powerzero,
            "int": intvmr,
            "VMR": VMR,
            "powermax": powermax,
            "centerindex": centerindex,
        }
        ints_desc = copy.deepcopy(ints)
        ints_desc["dark"] = "Measure of unpowered laser intensity"
        ints_desc["VMR"] = "Volume mixing ratio (ppmv)"
        ints_desc["int"] = "Raw integral of normalized spectra"
        ints_desc["powermax"] = "Highest laser intensity"
        ints_desc["centerindex"] = "Line Center Index"

        return [ints, ints_desc]

    def processEvents(self, updateInterval=0.1):
        """GUI updater.

		Used to update the GUI at a specified interval
		Unsure if this works
		"""
        updateInterval = 1.0
        try:
            self.time
        except:
            self.time = time.time()
        if time.time() - self.time > updateInterval:
            self.time = time.time()
            app.processEvents()
        else:
            return

    def linefits(self, ints, HK, scans, numDark, polyorder, numlines, wvlngthorder):
        """Spectral fitting module.

		Used to apply spectral fitting to distributed feedback
		laser scans.

		inputs:
			ints: dictionary of preprocessing run containing crude VMR
			HK: housekeeping dictionary
			scans: matrix containing scans
			numDark: number of bits of background measurement per scan
			polyorder: polynomial order of background fit
			numlines: Number of lines to fit?
			wvlgnthorder: polynomial order of wavelength dependence
		outputs:
			Tuple containing:
				fitparams: dictionary of fit parameters and results
				fitparamsDesc: description of the various fit parameters
		"""

        #modelType = "rautian"#"wofz"  # lor,gau,hit
        #modelType = "pseudo"#"wofz"  # lor,gau,hit
        modelType = "wofz"  # lor,gau,hit

        dims = scans.shape
        obs = dims[0]
        scanpts = dims[1]

        # SCANS[observation, points]
        x = np.arange(scanpts, dtype="float")
        # absscans = np.abs(scans)

        # removed powerzero (may need to add back for CLH-2 processing)
        if not self.newFmt:
            print("Removed powerzero removal")
            # powerzero = np.nanmean(scans[:, 4:35], 1)
            # Amended to use the zero averaged from ALL data
            powerzero = np.nanmean(scans[:, 5:35])
            #print(powerzero)
            # for i in range(obs):
            # 	scans[i,:] -= powerzero[i]
            scans -= powerzero
        else:
            powerzero = np.mean(scans[:, 15:35])
            if powerzero > 0.25:
                powerzero = 0.0
            # print(powerzero)
            # scans[:,:] -= 0.01
            scans[:, :] -= powerzero
            # scans[:,:] *= 1.0
        # scans = absscans

        # HK['normScale'] = HK['press']*0.0
        for i in range(obs):
        #    # 	HK['normScale'][i] = 1.0#np.linalg.norm(scans[i,:])
            scans[i,:] = np.abs(scans[i,:])
            #scans[i,:] = scans[i,:]/np.linalg.norm(scans[i,:])
        # scans[i,:] = scans[i,:] - 0.0025

        # left = 350
        if self.newFmt:
            left = 100  # 200
            right = 10
        else:
            left = numDark + 40#80#10#30  # 10#20#50
            right = 10#5  # 40#5#20

        if self.newFmt:
            lineset = 2
        else:
            lineset = 3

        if lineset == 0:
            lineCenter = np.array([467, 715, 503, 558, 0])
            wavelength = np.array(
                [2647.542486, 2647.673962, 2647.565197, 2647.594939, 2647.534453]
            )
            isoNum = np.array([11, 14, 12, 12, 13])
            intensity = np.array([4.276e-23, 1.63e-23, 7.581e-24, 1.332e-24, 4.99e-24])
            molMass = np.array([18, 19, 20, 20, 19])
            einsteinA = np.array([0.04193, 15.23, 0.4988, 0.2427, 7.173])
            airWidth = np.array([0.0808, 0.0918, 0.097, 0.0628, 0.0991])
            selfWidth = np.array([0.371, 0.5, 0.494, 0.391, 0.499])
            lowerStateEnergy = np.array([648.9787, 150.1562, 78.9886, 445.3462, 141.9024])
            tempDep = np.array([0.61, 0.69, 0.71, 0.61, 0.71])
            pressShift = np.array([-0.00789, 0.0, 0.0021, -0.0061, -0.00789])
            # mags = mags*1e20#*self.upscale #worked with e21
        elif lineset == 2:
            hitranArr = np.array(
                [
                    1,
                    1,
                    7286.050850,
                    2.050e-22,
                    0.3237,
                    0.0755,
                    0.458,
                    447.2523,
                    0.63,
                    -0.008249,
                ]
            )
            hitranArr = np.c_[
                hitranArr,
                np.array(
                    [
                        1,
                        2,
                        7285.770300,
                        3.442e-23,
                        8.427,
                        0.093,
                        0.51,
                        78.9886,
                        0.71,
                        -0.00696,
                    ]
                ),
            ]
            hitranArr = np.c_[
                hitranArr,
                np.array(
                    [
                        1,
                        1,
                        7285.667100,
                        2.462e-24,
                        9.003,
                        0.0922,
                        0.42,
                        1739.4837,
                        0.71,
                        -0.009640,
                    ]
                ),
            ]
            # with open('./ReducedHitran_1372.csv', 'r') as csvFile:
            with open("./config/ReducedHitran.csv", "r") as csvFile:
                spamreader = csv.reader(csvFile, delimiter=",")
                for i, row in enumerate(spamreader):
                    if i == 0:
                        continue
                    try:
                        tmprow = np.array([float(x) for x in row])
                        hitranArr = np.c_[hitranArr, tmprow]
                    except:
                        continue

            # lineCenter = np.array([880, 1275, 1400])#411, 281])
            lineCenter = np.array([850, 1250, 1400])  # 411, 281])
            # lineCenter = np.array([650, 1060, 1400])#411, 281])
            # lineCenter = np.array([750, 1100, 1400])#411, 281])
            # lineCenter = np.array([430, 714, 1400])#411, 281])
            # lineCenter = np.array([750, 1100, 1400])#411, 281])
            # lineCenter += 225
            lineCenterIndex = np.array([0, 1, 2])

        elif lineset == 3:
            hitranArr = np.array(
                [1, 1, 7306.7521, 1.795e-20, 8.861, 0.093, 0.51, 79.4964, 0.71, -0.00696]
            )
            
            #=(-S2-SQRT(S2*S2-4*(Q2-7306.7521)*U2))/(2*U2) #Excel calc for quickly computing line center.
            hitranArr = np.c_[
                hitranArr,
                np.array(
                    [
                        1,
                        1,
                        7306.48843,
                        1.271e-22,
                        0.2517,
                        0.1002,
                        0.51,
                        70.0908,
                        0.69,
                        -0.00318,
                    ]
                ),
            ]
            hitranArr = np.c_[
                hitranArr,
                np.array(
                    [
                        1,
                        1,
                        7306.73977,
                        1.009e-21,
                        0.886,
                        0.0747,
                        0.391,
                        325.3479,
                        0.36,
                        -0.00820,
                    ]
                ),
            ]

            with open('./config/ReducedHitran_1368.csv', 'r') as csvFile:
                #with open("./config/ReducedHitran.csv", "r") as csvFile:
                spamreader = csv.reader(csvFile, delimiter=",")
                for i, row in enumerate(spamreader):
                    if i == 0:
                        continue
                    try:
                        tmprow = np.array([float(x) for x in row])
                        hitranArr = np.c_[hitranArr, tmprow]
                    except:
                        continue

            # hitranArr = np.c_[hitranArr, np.array([1, 1, 7306.35384, 3.53E-23, 8.93 , 0.0944, 0.51, 136.3366, 0.69, -0.00326])]
            # lineCenter = np.array([275, 398, 281])#411, 281])
            lineCenter = np.array([280, 421, 287])  # 411, 281])
            lineCenterIndex = np.array([0, 1, 2])

        lineCenterWaveNum = np.array(
            [
                hitranArr[2, lineCenterIndex[0]],
                hitranArr[2, lineCenterIndex[1]],
                hitranArr[2, lineCenterIndex[2]],
            ]
        )

        # used to remove the duplicate main lines in window that were used for estimating window size
        hitranArr = hitranArr[:, 3:]

        # self.loadHitranKeys()

        # wvMin = 1368.53#1368.0#1372.0
        # wvMax = 1368.67#1369.0#1373.0

        # wvMin = 10000000/7310.25#7304.0#7312.0#7300.5#7310.0
        # wvMax = 10000000/7311.1#7309.0#7306.0#12.0#7297.5#7312.0
        wvMax = 10000000 / 7306.2  # .0#7312.0#7300.5#7310.0
        wvMin = 10000000 / 7307.2  # 7309.0#7306.0#12.0#7297.5#7312.0

        # wvMin = 10000000/7312
        # wvMax = 10000000/7310
        domain = np.linspace(10000000.0 / wvMin, 10000000.0 / wvMax, 1000)

        molecularInfoDict = loadHitranKeys()
        fullLines = [10000000 / (wvMin), 10000000 / (wvMax)]
        # readHitran last two args are a rolloff filter outside of window
        #   and a slope to increase the minimum cutoff per window width from
        # 	center of window.
        #hitran = readHitran(molecularInfoDict, fullLines, 1e4, 1e3)
        hitran = readHitran(molecularInfoDict, fullLines, 7e3, 1e4)
        #hitran = readHitran(molecularInfoDict, fullLines, 1e5, 1e3)

        #7306.79 is the main line.
        redHitran = readHitran(molecularInfoDict, fullLines, 5e2, np.inf)
        #hitran = readHitran(molecularInfoDict, fullLines, 5e3, 1e3)

        hitranPars = hitran

        numlines = len(hitran[:, 0])  # Pars[:,0])#wavelength)
        self.numLines.setValue(len(hitran[:, 0]))  # hitranPars[:,0]))

        # isoInc = 0
        # order of hitranPars is:
        # 	molMass, wavelength, intensity, einsteinA, airWidth,
        # 	selfWidth, lowerStateEnergy, tempDep, pressShift
        # hitranPars = np.c_[molMass, wavelength, intensity, einsteinA, airWidth, \
        # 	selfWidth, lowerStateEnergy, tempDep, pressShift, ppmvNum]

        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################

        # Number of isotopes to allow to vary....
        # This number should correspond to an array with isotopes that are allowed to float along an "adjusted ppmv".
        # If the iso number is not in the list, it is asserted to the primary isotope (11)
        isoVary = np.unique(hitranArr[:, 1])  # self.hitranPars[:,1])

        isoVary = np.sort(isoVary)

        # if len(isoVary) > 2:
        # 	isoVary = isoVary[:2]
        if len(isoVary) > 1:
            isoVary = isoVary[:1]

        # Assertion that only one isotopologue is allowed to vary (primary water)
        if not self.newFmt:
            isoVary = ["1_1"]#,"1_4"]
        else:
            isoVary = ["1_1", "1_2"]

        # isoVary = ["1_1", "1_4"]

        # isoVary = ['1_1','1_2']
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################

        pars = fitParsInit(wvlngthorder, polyorder, isoVary, ['offset'])

        # Used to determine approximate first guess for laser intensity relationship
        backSlope = np.mean(np.diff(scans[0, left:-right]))
        test = np.abs(scans[0, left:-right]) - np.abs(x[left:-right] * backSlope)
        backIntercept = np.max(test)
        backArr = [(backIntercept), (backSlope), 0.00, 0.00, 0.00, 0.00, 0.00]  # 1.0e-12]
        backMins = [-np.inf] * 6  # , -np.inf, -np.inf]
        backMaxs = [np.inf] * 6  # , np.inf, np.inf]
        for i in range(polyorder + 1):
            pars["back_c" + str(i)].set(value=backArr[i], vary=True)

        # Used to determine approximate first guess for wavelength relationship
        shiftSlope = (lineCenterWaveNum[1] - lineCenterWaveNum[0]) / (
            lineCenter[1] - lineCenter[0]
        )
        shiftIntercept = lineCenterWaveNum[0] - shiftSlope * lineCenter[0]
        if not self.newFmt:
            shiftSlope = -0.0017  # (1.89673e-3)
            shiftIntercept = (
                7307.22
            )  # 7300.0#7311.1#7307.25#7307.25#7311.1#7309.00#.25#7311.5#7300.0#7311.25#7.30726e3
        shiftArr = [shiftIntercept, shiftSlope, 0.0, 0.0, 0.0, 0.0]
        shiftSlope *= 4.0
        shiftMins = [-np.inf] * 5  # , -np.inf, -np.inf]
        shiftMaxs = [np.inf] * 5  # , np.inf, np.inf]
        for i in range(wvlngthorder + 1):
            pars["shift_c" + str(i)].set(
                value=shiftArr[i], vary=True
            )  # , min = shiftMins[i], max = shiftMaxs[i])#, vary = True)

        pars["conc_1_1"].set(value=5000)
        
        #pars["conc_1_4"].set(value=-100.0, max = 0.0, min = -1000.0)
        #except: pass

        # Figure initialization parameters
        self.figure.clear()
        nullSpec = np.zeros(len(x), dtype="float")
        ax = self.figure.add_subplot(111)
        line1, line2, line3, line4, line5, line6, line7, line8 = ax.plot(
            x,
            nullSpec,
            "k",
            x,
            nullSpec,
            "r",
            x,
            nullSpec,
            "b",
            x,
            nullSpec,
            "k",
            x,
            nullSpec,
            "y",
            x,
            nullSpec,
            "g",
            x,
            nullSpec,
            "m",
            x,
            nullSpec,
            "c",
        )
        ax2 = ax.twinx()
        line4, line5, line6, line7, line8 = ax2.plot(
            x,
            nullSpec,
            "k",
            x,
            nullSpec,
            "y",
            x,
            nullSpec,
            "g",
            x,
            nullSpec,
            "m",
            x,
            nullSpec,
            "m",
        )  # ,x[left:-right],nullSpectra,'m',

        # Initialize progress bar
        self.progress.setRange(0, obs)

        """
		extraLineParams = ['_integral','_pointwise','_center']
		#extraParams = ['chisqr','redchi','ndata','nvarys', 'nfev','success','ier','aic','bic']
		#extraParams = ['chisqr','ndata','nvarys', 'nfev','bic']
		extraParams = ['chisqr','ndata','nvarys', 'nfev','bic']#,'temp','press','path']
		envParams = ['temp','press','path']
		"""
        # Provide in [name, description] pairs such as ['_integral','_integral of the spectra']
        extraLineParams = [
            ["_integral", "Integral of the line"],
            ["_pointwise", "Boxcar estimation of peak height of absorption feature"],
            ["_center", "Bit index of absorption feature"],
        ]
        # extraParams = ['chisqr','redchi','ndata','nvarys', 'nfev','success','ier','aic','bic']
        # extraParams = ['chisqr','ndata','nvarys', 'nfev','bic']
        extraParams = [
            ["chisqr", "Statistical Chi-Square parameter"],
            ["ndata", "Number of data points in fit"],
            ["nvarys", "Nmber of degrees of freedom in fit"],
            ["nfev", "Number of function evaluations to converge to solution"],
            ["bic", "Bayesion information criterion"],
        ]  # ,'temp','press','path']
        envParams = [
            ["temp", "Temperature used in fit"],
            ["press", "Pressure used in fit"],
            ["path", "Path length used in fit"],
        ]
        diagParams = [
            ["lPower", "Peak laser power"],
            ["lPowerIndexCutoff", "Cutoff index avoiding saturation"],
            ["adaptiveAverage", "Number of spectra used in running average"],
            ["staticppmv", "Mixing ratio assuming no averaging"],
        ]

        fitparams = {}
        fitparamsDesc = {}
        for i in range(wvlngthorder + 1):
            fitparams["shift_c" + str(i)] = np.zeros(obs, dtype="float")
            fitparamsDesc[
                "shift_c" + str(i)
            ] = "Bit number to wavelength polynomial coefficient " + str(i)
            fitparams["shift_c" + str(i) + "_err"] = np.zeros(obs, dtype="float")
            fitparamsDesc["shift_c" + str(i) + "_err"] = (
                "Bit number to wavelength polynomial coefficient " + str(i) + " error"
            )
        for i in range(polyorder + 1):
            fitparams["back_c" + str(i)] = np.zeros(obs, dtype="float")
            fitparamsDesc[
                "back_c" + str(i)
            ] = "Laser power background polynomial coefficient " + str(i)
            fitparams["back_c" + str(i) + "_err"] = np.zeros(obs, dtype="float")
            fitparamsDesc["back_c" + str(i) + "_err"] = (
                "Laser power background polynomial coefficient " + str(i) + " error"
            )

        for par in envParams:
            fitparams[par[0]] = np.zeros(obs, dtype="float")
            fitparamsDesc[par[0]] = par[1]
            fitparams[par[0] + "_err"] = np.zeros(obs, dtype="float")
            fitparamsDesc[par[0] + "_err"] = par[1]

        # for i in range(len(isoVary)):#numlines):
        for id in isoVary:
            fitparams["conc_" + id] = np.zeros(obs, dtype="float")
            fitparamsDesc["conc_" + id] = "Mixing ratio derived from fit for line " + str(
                i
            )
            fitparams["conc_" + id + "_err"] = np.zeros(obs, dtype="float")
            fitparamsDesc[
                "conc_" + id + "_err"
            ] = "Mixing ratio error derived from fit for line " + str(i)
            fitparams["conc_" + id + "_center"] = np.zeros(obs, dtype="float")
            fitparamsDesc[
                "conc_" + id + "_center"
            ] = "Derived center index for line " + str(i)
            for vals in extraLineParams:
                fitparams["conc_" + id + vals[0]] = np.zeros(obs, dtype="float")
                fitparamsDesc["conc_" + id + vals[0]] = vals[1] + " " + str(i)
        # for i in range(numlines-1):
        # 	fitparams['del'+str(i)] = np.zeros(obs)
        for i in range(len(isoVary) - 1):
            fitparams["del" + str(i)] = np.zeros(obs, dtype="float")
            fitparamsDesc["del" + str(i)] = (
                "Isotope fractionation between isotope "
                + str(i)
                + " and isotope "
                + str(i + 1)
            )
        for vals in extraParams:
            fitparams[vals[0]] = np.zeros(obs, dtype="float")
            fitparamsDesc[vals[0]] = vals[1]

        for vals in diagParams:
            fitparams[vals[0]] = np.zeros(obs, dtype="float")
            fitparamsDesc[vals[0]] = vals[1]

        # wideDomain = np.arange(-scanpts, 2*scanpts, 1/10)

        # rc = np.zeros(numlines,dtype='int')
        abs_max = np.zeros(numlines, dtype="float")

        originalRight = right
        originalLeft = left

        # saturatedVoltage = 5  # 3.95
        saturatedVoltage = 3.95#75

        try:
            plotDivisions = int(self.plotDivisions.text())
        except:
            plotDivisions = 100
            self.plotDivisions.setText("100")
        if plotDivisions > obs:
            plotDivisions = obs
            self.plotDivisions.setText(str(round(obs)))
        
        winsound.Beep(1500, 4000)        
            
        secondPassBool = np.zeros(obs, dtype="int")
        for i in range(obs):#8500,obs):
            # if round(i*plotDivisions/obs) == i/np.floor(obs/plotDivisions):# or intvmr[i]>100:
            if i % int(np.floor(obs / plotDivisions)) == 0:  # or intvmr[i]>100:
                self.progress.setValue(i + 1)
                
            right = originalRight
            left = originalLeft
            
            # while np.abs(scans[i,-right]*HK['normScale'][i]) > saturatedVoltage and np.abs(scans[i,-right]*HK['normScale'][i]) <= np.abs(scans[i,-(right+2)]*HK['normScale'][i]) and right <= 200:
            
            #Official code for finding the cutoff 
            #while (
            #    np.abs(scans[i, -right]) > saturatedVoltage
            #    and np.abs(scans[i, -right]) <= np.abs(scans[i, -(right + 2)])
            #    and right <= 200
            #    ):
                
            #smoothedScan = smoothingFunction(scans[i,:], points=11, repeat=3, method="savgol")
            #smoothedScan = smoothingFunction(scans[i,:], points=3, repeat=1, method="savgol")
            #smoothedScan = scans[i,:]#smoothingFunction(scans[i,:], points=7, repeat=8, method="savgol")
            smoothedScan = smoothingFunction(scans[i,:], points=11, repeat=4, method="savgol")


            while (
                np.abs(scans[i,-right]) > saturatedVoltage or np.nanmean(np.abs(smoothedScan[-5])) < np.nanmean(np.abs(smoothedScan[-right-5]))
               ):
            
            #while (
            #    np.mean(np.abs(scans[i,-right-6:-right+4])) < np.mean(np.abs(scans[i,-right-10:-right])) and right <= 200
            #):
            
            ######## Way to find the right cutoff by looking at the slope of the line, if slope negative keeping moving ####

            #while (
            #    np.mean(np.diff(np.abs(smoothedScan[-right-10:]))) <= 0 and right <= 200
            #):
                right += 1
            
            #### Chosen to add additional buffer to the right padding to avoid soft inflection regime ######
            if right != originalRight: right += 20
            
            # if np.abs(scans[i,-right]*HK['normScale'][i]) > saturatedVoltage:
            #if np.abs(scans[i, -right]) > saturatedVoltage:
            #    # while np.abs(scans[i,-right]*HK['normScale'][i]) > saturatedVoltage and right <= 200:
            #    while np.abs(scans[i, -right]) > saturatedVoltage and right <= 200:
            #        right += 1
            #print(left,right)

            if self.newFmt:
                left = originalLeft
                right = originalRight

                backSlope = np.mean(np.diff(scans[i, left:-right]))
                test = np.abs(scans[i, left:-right]) - np.abs(x[left:-right] * backSlope)
                backIntercept = np.max(test)

                pars["back_c0"].set(value=backIntercept, vary=True)
                pars["back_c1"].set(value=backSlope, vary=True)

            ####################################################################################
            ####################################################################################
            ####################################################################################
            ####################################################################################

            # Added for JPL experiment
            # right = originalRight

            vals = 0
            # for vals in range(1):#numlines):
            if self.newFmt:
                # pars['press'].set(value = HK['press'][i]+14.2, min = 1, max = 2000, vary = True)
                pars["press"].set(
                    value=HK["press"][i], min=1, max=2000, vary=False
                )  # True)
                # pars['temp'].set(value = HK['temp1'][i]+0.33, min = -10, max = 100, vary = False)#True)
                pars["temp"].set(
                    value=HK["temp1"][i], min=-10, max=100, vary=False
                )  # True)
                # Set temperature to 25 for JPL tests, revert to line above for all else
                pars["path"].set(value=7600.0, min=4000, max=10000, vary=False)  # True)
                # pars['path'].set(value = 7600.0, min = 4000, max = 10000, vary = False)#True)
            else:
                pars["press"].set(
                    value=HK["press"][i], min=1, max=2000, vary = False
                )  # True)
                
                #June 2019 MKS Calibration, supposedly not correct for SOCRATES but worth trying?
                #P(true, in mbar) = P(reading)*0.9353 - 1.4
                #pars["press"].set(value = HK["press"][i]/0.9353 - 1.4, vary = False)

                # pars['path'].set(value = 52.0, vary = False)#True)
                # Calibrated path length...
                #pars["path"].set(value=48.0, vary=False)
                #pars['path'].set(value = 53.3)
                #Path attempt to remove calibration requirement
                pars["path"].set(value=48.0, vary = False)
                pars["temp"].set(value=(HK["temp1"][i] + HK["temp2"][i]) / 2.0, vary=False)

            pars["conc_1_1"].set(vary = True)#min=0.0, max=1e6, vary=True)
            # pars['conc_1_2'].set(min = 0.0, max = 1e6, vary = True)
            #pars["conc_1_4"].set(vary = False, value = -1, max = 0.0, min = -1000.0)

            try:
                lastValidPars
            except:
                lastValidPars = pars

            try:
                if HK["press"][i] < 200.0:#100.0:
                    #print("Low Pressure Flag")
                    logging.debug("Low Pressure Flag")
                    raise
                # I need to go about limiting the iteration number to prevent long runs
                # c1 = -0.00165 works quite well with rautian.
                pars["shift_c1"].set(vary=False, value = -0.00185)#178)#175)#5)#8)#, value = -0.00145)   
                pars["shift_c0"].set(vary=True, value = 7307.23)#, max = 7307.3, min = 7307.18)
                pars["shift_c2"].set(vary=False, value = 0)#-1.0e-9)
                
                #try: pars["shift_c2"].set(value = 0.0)#, max = 5e7, min = -5e-7)
                #except: pass
                
                #pars['press'].set(vary = True, min = 10, max = 1500)
                pars["back_c2"].set(value = 0.0, vary = True)
                #try: pars['shift_c2'].set(value = 0.0, vary = False)#True)
                #except: pass
                
                #try: pars['back_c3'].set(value = 0.0, vary = True)
                #except: pass  
                #pars["back_c3"].set(vary = True)

                #(-S2-SQRT(S2*S2-4*(Q2-7306.7521)*U2))/(2*U2)

                '''
                # Check to see if last run had good data
                try:
                    if (
                        out.params["conc_1_1"].value < 3000
                        or out.params["conc_1_1"].value > 30000#10000
                        or out.params["press"].value < 400#250
                        or out.params["press"] > 900#750
                    ):
                        if ints["VMR"][i] - 1000 < 100:
                            pars['conc_1_1'].set(value = 100)#
                        else:
                            pars['conc_1_1'].set(value = ints["VMR"][i] - 1000)
                        #pars["shift_c0"].set(vary=True)
                        #pars["shift_c1"].set(vary=False, value = -0.0018)
                        #pars["back_c0"].set(vary = False)
                        #pars["back_c2"].set(vary = False)
                        #pars["back_c3"].set(vary = False)
                        #pars["shift_c2"].set(vary=False)
                except:
                    pass
                '''
                
                #if ints["VMR"][i] - 1200 < 10:
                #    pars['conc_1_1'].set(value = 10)#
                #else:
                #    pars['conc_1_1'].set(value = ints["VMR"][i] - 100)
                    
                ##### Routine to take raw mixing ratios (old codes) bring to a zero point,
                ##### then use as a guess for the calculations ####
                    
                    
                ########################################################
                ############## PRIMARY FITTING ROUTINE #################
                ########################################################
                #smoothedScan = smoothingFunction(scans[i,:], points=3, repeat=5, method="convolve")
                
                ### Deprecated cutoff for small signals.
                #if(ints["VMR"][i]<2000): 
                #    left = 150
                #    if right < 120: right = 120
                    
                    
                ##### Dumb background adjustment to fuck with the endpoints #####
                rr = 512 - right
                
                #redx = x[left:-right]
                #smoothedScan = smoothingFunction(scans[i,:], points=7, repeat=8, method="savgol")
                
                superSmoothed = smoothedScan
                #smoothingFunction(scans[i,:], points=31, repeat=3, method="savgol")
                
                twoPtSlope = (superSmoothed[-right] - superSmoothed[left])/(x[-right]-x[left])
                twoPtInt = (superSmoothed[left] - twoPtSlope*x[left])
                twoPtLine = x*twoPtSlope + twoPtInt

                #superSmoothedDif = np.diff(superSmoothed)#/twoPtLine)
                #superSmoothedGrad = np.gradient(superSmoothed)#/twoPtLine)
                
                #print(superSmoothedGrad[::8])
                
                ##### Find greatest deviation of smoothed scan from actual line ######
                try:
                    lastCenter = int(domShiftInv(
                        out.params, 7306.7521#hitranPars[0, 3]
                    ))
                except:
                    lastCenter = 280
                
                hardLeft = left
                hardRight = right
                
                #superSmoothed = superSmoothed[i, left:-right][::1]
                
                #### If the max peak deviation is greater than the minimum deviation ####
                #### I know that the signal is strong? ####
                #if max(1-smoothedScan[left:-right]/twoPtLine[left:-right]) < min(1-smoothedScan[left:-right]/twoPtLine[left:-right]):
                #pp = abs(min(smoothedScan[left:-right]/twoPtLine[left:-right] - 1) - min(smoothedScan[left:-right]/twoPtLine[left:-right] - 1))
                #print(superSmoothedGrad)
                
                #secDeriv = np.gradient(smoothingFunction(scans[i,:], points=31, repeat=5, method="savgol"))
                #secDeriv = smoothingFunction(secDeriv,points=31,method="savgol")
                
                #gradMinLeft = int(np.argmin(secDeriv[left:lastCenter-10])) + left
                #gradMinRight = int(x[-1]) - (int(np.argmin(secDeriv[lastCenter+10:-right])) + lastCenter + 10)
                
                #hillSplit = (x[-gradMinRight] - gradMinLeft)
                #betweenHills = int(hillSplit/2) + gradMinLeft
                #print(betweenHills, hillSplit, gradMinLeft, gradMinRight)
                
                #print(gradMinLeft,gradMinRight)
                
                #### ESTIMATED PEAK ####
                #print(int(np.argmin(secDeriv[left:-right]))+left)
                
                if np.nansum(superSmoothed[left:-right]/twoPtLine[left:-right] - 1) > 0:
                    #abs(max(superSmoothed[:]/twoPtLine[:] - 1)) > abs(min(superSmoothed[:]/twoPtLine[:] - 1)):
                    #### Find greatest negative value on either side of peak ######
                    #print('did something')
                    #left = gradMinLeft#int(np.argmin(superSmoothedGrad[left:lastCenter])) + left
                    #right = gradMinRight#int(x[-1]) - (int(np.argmin(superSmoothedGrad[lastCenter:-right])) + lastCenter)
                    
                    left = 160
                    if right < 130: right = 130
                    
                    
                    #left = int(np.argmax(superSmoothed[left:lastCenter-20]/twoPtLine[left:lastCenter-20])) + left
                    #right = int(x[-1]) - (int(np.argmax(superSmoothed[lastCenter + 20:-right]/twoPtLine[lastCenter + 20:-right])) + lastCenter + 20)
                
                    #### The new left and right should be roughly the halfwidths.
                    #if lastCenter - 2*np.abs(lastCenter - left) >= hardLeft: left = lastCenter - 2*np.abs(lastCenter - left)
                    #if left - 20 >= hardLeft: left -= 20
                    #if lastCenter + 2*np.abs(lastCenter - x[-right]) <= x[hardRight]: right = int(x[-1]) - (lastCenter - 2*np.abs(lastCenter - x[-right]))
                    #if right - 20 <= hardRight: right -= 20
                    
                    #try: pars['shift_c2'].set(value = -1.5e-7, vary = False)#0.0, vary = False)
                    #except: pass
                    hitran2Use = redHitran
                
                '''
                else:
                    while True:
                        try:
                            if smoothedScan[left+10] >= twoPtLine[left+10] or left > 200: raise
                        except: break
                        #if smoothedScan[left+10] >= twoPtLine[left+10] or left > 200: break
                        left += 1
                    left += 1

                    while True:
                        try:
                            if smoothedScan[-right-10] >= twoPtLine[-right-10] or right > 150: raise
                        except: break
                        right += 1
                    
                    right += 1
                '''
                                    
                #print(lastCenter, 'Left: ',left,'\t Right:',right)
                    
                #smoothedScan = smoothingFunction(scans[i,:], points=7, repeat=8, method="savgol")
                #smoothedScan = smoothingFunction(scans[i,:], points=15, repeat=1, method="savgol")
                    
                scan2Use = smoothedScan[left:-right]
                #scan2Use = scans[i, left:-right][::1]
                hitran2Use = hitran
                
                #backSlope = (scan2Use[-1]-scan2Use[0])/(x[-right]-x[left])
                #backSlope = np.mean(np.diff(scan2Use))
                #test = np.abs(scan2Use) - np.abs(x[left:-right] * backSlope)
                #pars['back_c0'].set(value = np.max(test))
                #pars['back_c1'].set(value = backSlope)
                    
                #else: scan2Use = scans[i,left:-right]
                #try:
                #    pars['offset'].set(value = 0.0, vary = True)
                #except: pass
                
                #### CLH-2 Empirical background curve.
                clh_c2 = -2.71679E-06
                clh_c1 = 8.95621E-03
                clh_c0 = 3.56112E-01
                
                clh_c2 = -3.17485E-06
                clh_c1 = 9.20839E-03
                clh_c0 = 3.26915E-01
                
                clh_c2 = -2.62386E-06
                clh_c1 = 8.20926E-03
                clh_c0 = 3.04168E-01
                
                clhPowCurve = clh_c0 + clh_c1*x + clh_c2*np.power(x,2)
                
                pars["offset"].set(value=0.0, vary=False)#True)
                
                pars["back_c0"].set(value = 0.0, vary = True)#False)
                pars["back_c1"].set(value = smoothedScan[100]/clhPowCurve[100], vary = True)
                pars["back_c2"].set(value = 0.0, vary = False)

                try:
                    pars['conc_1_1'].set(value = out.params['conc_1_1'].value)
                    pars['back_c0'].set(value = out.params['back_c0'].value)
                    pars['back_c1'].set(value = out.params['back_c1'].value)
                    pars['back_c2'].set(value = out.params['back_c2'].value)
                    #pars['offset'].set(value = out.params['offset'].value, vary = True)
                    #pars['shift_c0'].set(value = out.params['shift_c0'].value, vary = True)
                    #pars['shift_c1'].set(value = out.params['shift_c1'].value, vary = True)
                    #pars['back_c3'].set(value = out.params['back_c3'].value)#, vary = False)#True)
                    #pars['press'].set(vary=True)
                    #del out
                    #del lastPars
                except: 
                    print('some dumb error')
                    pass
                    
                #if(ints["VMR"][i] > 20000):
                #    pars['back_c2'].set(vary=False)
                #else:
                #    pars['back_c2'].set(vary=True)
               
                #pars['back_c2'].set(value = -2e-6,vary=False)
               
                '''
               
                if(ints["VMR"][i]<2000):
                    pars['shift_c2'].set(vary=False)
                    #try: pars['shift_c2'].set(value = -1.5e-7, vary = False)#0.0, vary = False)
                    #except: pass
                    try: hitran2Use = redHitran
                    except: pass
                '''   
                
                
                out = minimize(
                    spectralWrapper,
                    pars,
                    args=(x[left:-right][::1],),
                    kws={
                        "molecularInfoDict": molecularInfoDict,
                        "data": scan2Use[::1],#smoothedTest[left:-right],#scans[i, left:-right][::1],
                        "hitran": hitran2Use,
                        "current": clhPowCurve[left:-right],
                        "modelType": modelType,
                    },
                    scale_covar=True,
                    method="leastsq"
                )  # ,\
                #"current": clhPowCurve[left:-right],
                '''


                worker = Worker( minimize )
                self.threadVar = None
                worker.signals.result.connect(self.workerVariableHold)
                #worker.signals.finished.connect(self.thread_complete)

                # Execute
                self.threadpool.start(worker (
                    spectralWrapper,
                    pars,
                    args=(x[left:-right][::1],),
                    kws={
                        "molecularInfoDict": molecularInfoDict,
                        "data": scan2Use,#smoothedTest[left:-right],#scans[i, left:-right][::1],
                        "hitran": hitran2Use,
                        "modelType": modelType,
                    },
                    scale_covar=True,
                    method="leastsq"
                )  # ,\) # Any other args, kwargs are passed to the run function
                ) 
                
                while( self.threadVar is None):
                    app.processEvents()
                    
                self.threadpool.stop()
                '''


                fitparams["staticppmv"][i] = out.params["conc_1_1"].value
                
                #fitparams["domShiftInv(pars, x)

                ############################# BEGIN ADAPTIVE AVERAGE ##############################################
                
                
                '''
                percentError = out.params['conc_1_1'].stderr*100.0/out.params['conc_1_1'].value
                #Limits to prevent huge averaging window
                if percentError > 3: percentError = 3
                if percentError >= 0.33 or percentError == 0:# and percentError != 0 and out.params['voigt0_ppmv'].value < 1000:
                    option = 1
                    if option == 1:
                        #Subroutine to increase averaging window to get lower noise at lower values.
                        #Multiply percent error to increase desired window size
                        windowWidth = int(np.round(percentError * 3))
                        fitparams['adaptiveAverage'][i] = windowWidth*2 + 1
                        #Add constraints for beginning and ends of range
                        if i < windowWidth: windowWidth = i
                        if (obs - i - 1) < windowWidth: windowWidth = (obs - i - 1)
                        #testOut = minimize(spectralWrapper, pars, args = (x[left:-right][::1],),\
                        #    kws = {'molecularInfoDict':molecularInfoDict,\
                        #    'data':np.mean(scans[i - windowWidth: i + windowWidth + 1,left:-right][::1],0),\
                        #    'hitran':hitran,'modelType': modelType},
                        #    scale_covar = True, method = 'leastsq')#,\
                            
                        ##### The above works to average enough spectra to get decent fit params #####
                        ##### So should take those values, and allow a reasonable fit back upon a smoothed spectra ######
                        
                        ##### Test smoothed spectra #####
                        smoothedTest = smoothingFunction(scans[i,:], points=5, repeat=10, method="convolve")
                        smoothedTest = smoothedTest[left:-right]
                        
                        try: pars['shift_c2'].set(value = 0.0, vary = False)
                        except: pass
                        
                        out = minimize(spectralWrapper, pars, args = (x[left:-right][::1],),\
                            kws = {'molecularInfoDict':molecularInfoDict,\
                            'data':scans[i,left:-right][::1],\
                            'hitran':hitran,'modelType': modelType},
                            scale_covar = True, method = 'leastsq')#,\   
                            
                        try: pars['shift_c2'].set(value = 0.0, vary = True)
                        except: pass
                        
                        
                        #line1.set_xdata(x[left:-right])
                        #line1.set_ydata(scans[i, left:-right]/laserBackground(out.params, x[left:-right])  -1)
                        #line2.set_xdata(x[left:-right])
                        #line2.set_ydata(smoothedTest/laserBackground(out.params, x[left:-right])-1)
                        
                        #ax.relim()
                        #ax2.relim()
                        #ax.autoscale_view()
                        #ax2.autoscale_view()

                        #self.figure.subplots_adjust(
                        #    left=0.05, right=0.95, bottom=0.05, top=0.99
                        #)
                        #ax.axis("tight")
                        #ax2.axis("tight")
                        #self.canvas.draw()
                            
                        print('successful run of low error prone fit')
                            
                    elif option == 2:
                        #Option to constrain fit to use decent background estimates
                        for j in range(wvlngthorder+1):
                            pars['shift_c'+str(j)].set(value = lastValidPars['shift_c'+str(j)].value, vary = False)#True)
                        for j in range(polyorder+1):
                            pars['back_c'+str(j)].set(value = lastValidPars['back_c'+str(j)].value, vary = False)#True)
                        pars['back_c0'].set(vary = True)
                        pars['back_c1'].set(vary = True)
                        pars['shift_c0'].set(vary = True)
                        out = minimize(spectralWrapper, pars, args = (x[left:-right][::1],),\
                            kws = {'molecularInfoDict':molecularInfoDict,'data':scan[left:-right][::1],\
                            'hitran':hitran,'modelType': modelType},
                            scale_covar = True, method = 'leastsq')#,\

                elif percentError < 0.33 and percentError != 0:
                    lastValidPars = out.params
                    #Segment to keep track of when "good" fitting values have been attained
                    #percentError = out.params['voigt0_ppmv'].stderr*100.0/out.params['voigt0_ppmv'].value
                    for j in range(wvlngthorder+1):
                        pars['shift_c'+str(j)].set(value = out.params['shift_c'+str(j)].value, vary = True)
                    for j in range(polyorder+1):
                        pars['back_c'+str(j)].set(value = out.params['back_c'+str(j)].value, vary = True)
                '''
                ############################### END ADAPTIVE AVERAGE #######################################        
                        

                if (
                    out.params["conc_1_1"].value > 3000
                    #5-19-2020 Changed 10000 to 30000
                    and out.params["conc_1_1"].value < 30000
                    and out.params["press"].value > 300
                    and out.params["press"].value < 800
                ):
                    goodRegion = True
                else:
                    goodRegion = False

                for j in range(wvlngthorder + 1):
                    pars["shift_c" + str(j)].set(vary=True)
                    if goodRegion:
                        pars["shift_c" + str(j)].set(value=out.params["shift_c" + str(j)])
                for j in range(polyorder + 1):
                    pars["back_c" + str(j)].set(vary=True)
                    if goodRegion:
                        pars["back_c" + str(j)].set(value=out.params["back_c" + str(j)])
                # for j in range(0, len(isoVary)):
                for id in isoVary:
                    pars["conc_" + id].set(
                        value=out.params["conc_" + id].value,
                        min=0.0,
                        max=1000000,
                        vary=True,
                    )

                    # pars['voigt'+str(j)+'_ppmv'].set(value = out.params['voigt'+str(j)+'_ppmv'].value, min = 0.0, max = 1000000, vary = True)

                #print(fit_report(out.params))
                # Code for isotopes?
                # for j in range(0, len(isoVary)):
                # 	pars['voigt'+str(j)+'_ppmv'].set(value = 10000.0, min = 0.0, max = 1e6, vary = True)
                # for j in range(wvlngthOrder+1):
                # 	pars['shift_c'+str(j)].set(value = out.params['shift_c'+str(j)].value, vary = True)
                # lastValidPars = out.params

                """
				try:
					for j in range(1,wvlngthorder+1):
						pars['shift_c'+str(j)].set(value = lastValidPars['shift_c'+str(j)].value, vary = False)
					#Need to allow to peak to walk to prevent complete nonsense when the laser walks
					pars['shift_c0'].set(value = lastValidPars['shift_c0'].value, vary = True)
					for j in range(polyorder+1):
						pars['back_c'+str(j)].set(value = lastValidPars['back_c'+str(j)].value, vary = True)#False)
					for j in range(0, len(isoVary)):
						#pars['voigt'+str(j)+'_ppmv'].set(value = 2000.0, min = 0.1, max = 200000, vary = True)#, min = 0, max = 200000, vary = True)#min = 0, max = 200000, vary = True)
						#pars['voigt'+str(j)+'_ppmv'].set(value = ints['VMR'][i], min = 0.1, max = 200000, vary = True)#, min = 0, max = 200000, vary = True)#min = 0, max = 200000, vary = True)
						pars['voigt'+str(j)+'_ppmv'].set(value = 2000, min = 0.0, max = 1000000, vary = True)#, min = 0, max = 200000, vary = True)#min = 0, max = 200000, vary = True)
						#pars['voigt'+str(0)+'_ppmv'].set(value = 2000.0, min = 1, vary = True)#, min = 0, max = 200000, vary = True)#min = 0, max = 200000, vary = True)
				except: pass
				"""

                """
				if not self.newFmt:
					percentError = out.params['voigt0_ppmv'].stderr*100.0/out.params['voigt0_ppmv'].value
					if percentError > 3: percentError = 3
					if percentError >= 0.33 and percentError != 0 and out.params['voigt0_ppmv'].value < 1000:
						secondPassBool[i] = 1

						percentError *= 3
						percentError = int(np.round(percentError))
						if i < percentError: percentError = i
						if (obs - i - 1) < percentError: percentError = (obs - i - 1)
						out = minimize(self.spectralModel, pars, args = (x[left:-right],),\
							kws = {'data':np.mean(scans[i - percentError: i + percentError + 1,left:-right],0),'hitran':hitranPars}, \
							scale_covar = True)#, method = 'trust-exact')#, reduce_fcn = 'None')

						#print(out.params)
						for j in range(0, len(isoVary)):
							pars['voigt'+str(j)+'_ppmv'].set(value = out.params['voigt'+str(j)+'_ppmv'].value, min = 0.0, max = 1000000, vary = True)
						for j in range(wvlngthorder+1):
							pars['shift_c'+str(j)].set(value = out.params['shift_c'+str(j)].value, vary = False)#True)
						for j in range(polyorder+1):
							pars['back_c'+str(j)].set(value = out.params['back_c'+str(j)].value, vary = False)#True)

						out = minimize(self.spectralModel, pars, args = (x[left:-right],),\
							kws = {'data':scans[i,left:-right],'hitran':hitranPars}, \
							scale_covar = True)#, method = 'trust-exact')#, reduce_fcn = 'None')
						#print(out.params)

					else: percentError = 0


					####ADD Section for bring the calculation back to the original scanning rate...
					### i.e. use solution from large average to input guesses for original...

					fitparams['adaptiveAverage'][i] = percentError*2 + 1
				"""

                # can add method = 'trust-exact' or various to parameters
                # try:
                # for coef in range(wvlngthorder+1):
                # 	pars['shift_c'+str(coef)].set(value = out.params['shift_c'+str(coef)])

                # for val in wvNumbers:
                # 	if self.domShiftInv(out.params,val) < 200 or self.domShiftInv(out.params,val) > 450:

                # print("Chi Squared Result: ",out.chisqr)
                # if round(i*plotDivisions/obs) == i/np.floor(obs/plotDivisions):# or intvmr[i]>100:

                # print(fit_report(out)) #	print(val," corresponds to: ",self.domShiftInv(out.params,val))

                if (
                    i % int(np.floor(obs / plotDivisions)) == 0
                ):  # or out.params['voigt0_ppmv'].value < 500.0:# or intvmr[i]>100:
                    # print(fit_report(out))
                    logging.debug(fit_report(out))
                    scaling = 1.0
                    # print('New Left:  ',left)
                    # print('New Right: ',right)

                    line1.set_xdata(x[:])
                    # line1.set_ydata(self.spectralModel(out.params, x[:], hitranPars))

                    line1.set_ydata(
                        spectralWrapper(out.params, x[:], hitran, molecularInfoDict,current=clhPowCurve)
                    )
                    line2.set_xdata(x[:])
                    line2.set_ydata(scans[i, :])
                    line3.set_xdata(x[:])

                    #currentBackground = laserBackground(out.params, x[:])
                    currentBackground = laserBackground(out.params, clhPowCurve)
                    line3.set_ydata(currentBackground)

                    # line3.set_ydata(self.laserBackground(out.params, x[:]))

                    # derpy = diff(self.laserBackground(out.params, x[:]))
                    # for indexy, derp in enumerate(derpy):
                    # 	print(derp)

                    line4.set_xdata(x[:])
                    line5.set_xdata(x[:])
                    line6.set_xdata(x[:])
                    line7.set_xdata(x[:])
                    line8.set_xdata(x[:])

                    normScan = -scaling * np.log(scans[i, :] / currentBackground)
                    normScan[np.where(normScan > np.max(normScan[left:-right]))] = 0.0
                    normScan[np.where(normScan < 0)] = 0.0

                    tmp = -np.log(scans[i, :] / currentBackground)
                    tmp[: left + 10] = np.nan
                    line5.set_ydata(tmp)  # s(scans[i,left:]/currentBackground[left:]))
                    tmp = -np.log(smoothedScan/currentBackground)
                    tmp[: left + 10] = np.nan
                    line6.set_ydata(tmp)
                    
                    #line4.set_ydata(scans[i,left:]/currentBackground[left:])
                    #line5.set_ydata(1 - scaling * self.spectralModel(out.params, self.domShift(out.params,x[:]), hitranPars, True,0))
                    #line5.set_ydata(1 - scaling * spectralWrapper(out.params, domainShift(out.params,x[:]), hitran, molecularInfoDict, True,0))
                    line7.set_ydata(-np.log(spectralWrapper(out.params, x[:], hitran, molecularInfoDict,current=clhPowCurve)/currentBackground))
                    #spectralWrapper(out.params, x[:], hitran, molecularInfoDict)
                    #tmp = np.log(
                    #    0
                    #    - np.log(
                    #        spectralWrapper(
                    #            out.params,
                    #            domainShift(out.params, x[:]),
                    #            hitran,
                    #            molecularInfoDict,
                    #            True,
                    #            0,
                    #        )
                    #    )
                    #)
                    #tmp[: left + 10] = np.nan
                    #line5.set_ydata(tmp)
                    # line5.set_ydata(1 - spectralWrapper(out.params, domainShift(out.params,x[:]), hitran, molecularInfoDict, True,0))
                    # line5.set_ydata(1 - scaling * spectralWrapper(out.params, domainShift(out.params,x[:]), hitran, molecularInfoDict, True,0))

                    # locate indices for first three strongest lines from center of derived window
                    windowHW = scanpts / 2.0 * out.params["shift_c1"].value
                    windowCenter = (
                        out.params["shift_c0"].value + windowHW
                    )  # scanpts/2.0 * out.params('shift_c1')
                    windowHW = np.abs(windowHW)

                    """
					inWinLines = np.where(np.logical_and(hitranPars[:,3]>windowCenter-windowHW, \
						hitranPars[:,3]<windowCenter+windowHW))[0]
					firstMax = np.max(hitranPars[inWinLines,4])
					firstLine = np.where(hitranPars[:,4] == firstMax)[0]
					inWinLines = np.where(np.logical_and(np.logical_and(hitranPars[:,3]>windowCenter-windowHW, \
						hitranPars[:,3]<windowCenter+windowHW), hitranPars[:,4] < firstMax))[0]
					secMax = np.max(hitranPars[inWinLines,4])
					secLine = np.where(hitranPars[:,4] == secMax)[0]
					inWinLines = np.where(np.logical_and(np.logical_and(hitranPars[:,3]>windowCenter-windowHW, \
						hitranPars[:,3]<windowCenter+windowHW), hitranPars[:,4] < secMax))[0]
					thirdMax = np.max(hitranPars[inWinLines,4])
					thirdLine = np.where(hitranPars[:,4] == thirdMax)[0]

					firstLine = firstLine[0]
					secLine = secLine[0]
					thirdLine = thirdLine[0]
					"""

                    # if numlines > 1: line6.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,firstLine))
                    # if numlines > 2: line7.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,secLine))
                    # if numlines > 3: line8.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,thirdLine))

                    """
					if numlines > 1: line6.set_ydata(1 - scaling * spectralWrapper(out.params,domainShift(out.params,x[:]),hitran, molecularInfoDict,True,firstLine))
					if numlines > 2: line7.set_ydata(1 - scaling * spectralWrapper(out.params,domainShift(out.params,x[:]),hitran, molecularInfoDict,True,secLine))
					if numlines > 3: line8.set_ydata(1 - scaling * spectralWrapper(out.params,domainShift(out.params,x[:]),hitran, molecularInfoDict,True,thirdLine))
					"""

                    # if numlines > 1: line6.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True))
                    # if numlines > 1: line6.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,1))
                    # if numlines > 2: line7.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,2))
                    # if numlines > 3: line8.set_ydata(1 - scaling * self.spectralModel(out.params,self.domShift(out.params,x[:]),hitranPars,True,3))

                    ax.relim()
                    ax2.relim()
                    ax.autoscale_view()
                    ax2.autoscale_view()

                    ims = []
                    if (len(isoVary)) == 1:
                        ims.append([line1, line2, line3, line4])
                    # if numlines == 2: ims.append([line1,line2,line3,line4,line5])
                    # if numlines == 3: ims.append([line1,line2,line3,line4,line5,line6])
                    # if numlines == 4: ims.append([line1,line2,line3,line4,line5,line6,line7])

                    self.figure.subplots_adjust(
                        left=0.05, right=0.95, bottom=0.05, top=0.99
                    )
                    ax.axis("tight")
                    ax2.axis("tight")
                    self.canvas.draw()
                    # app.processEvents()
                self.processEvents()

                for key, value in fitparams.items():
                    find = False
                    for val in extraLineParams + extraParams + ["del"] + diagParams:
                        if val[0] in key:
                            find = True
                    if not find:
                        if "_err" not in key:
                            fitparams[key][i] = out.params[key].value
                            fitparams[key + "_err"][i] = out.params[key].stderr
                            # print(fitparams[key][i])
                        # if out.params[key].value == pars[key].value and out.params[key].vary : input("warning: failure to iterate value: "+key)
                        # if out.params[key] <= pars[key].min + (pars[key].max - pars[key].min)/10000 and out.params[key].vary and 'shift_c1' not in key: input("warning: value pinned to min: "+key)
                        # if out.params[key] >= pars[key].max - (pars[key].max - pars[key].min)/10000 and out.params[key].vary and 'shift_c1' not in key: input("warning: value pinned to max: "+key)
                        # print(out.params[key].value)
                    find = False

                    # if not any(x in key for x in (['del']+extraLineParams + extraParams)):
                    # 	print(key)
                    # 	fitparams[key][i] = vars(out)[key]

                fitparams["lPower"][i] = np.max(scans[i, :])
                fitparams["lPowerIndexCutoff"][i] = scanpts - right

                for key in extraParams:
                    fitparams[key[0]][i] = vars(out)[key[0]]

                # if fitparams['voigt0_ppmv_err'][i]/fitparams['voigt0_ppmv'][i]*100 > 20 or fitparams['voigt0_ppmv_err'][i] == 0:
                # 	fitparams['voigt0_ppmv'][i] = -9999

                # for vals in range(numlines):
                # 	fitparams['voigt'+str(vals)+'_center'][i] = self.domShiftInv(out.params,fitparams['voigt'+str(vals)+'_center'][i])
                # 	a.append(fitparams['voigt'+str(vals)+'_center'][i])
                # a = []
                # for vals in range(numlines):
                # 	fitparams['voigt'+str(vals)+'_integral'][i] = integrate.quad(lambda z: self.spectralModel(out.params, z, True, vals), wvlngths[vals]-2, wvlngths[vals]+2)[0]
                # 	a.append(fitparams['voigt'+str(vals)+'_integral'][i])
                # print('integrals: ',a)

                # for val in range(len(isoVary)):
                for id in isoVary:
                    try:
                        fitparams["conc_" + id + "_center"][i] = domShiftInv(
                            out.params, 7306.7521#hitranPars[0, 3]
                        )
                        #print(fitparams["conc_1_1_center"][i])
                    except:
                        fitparams["conc_" + id + "_center"][i] = -9999

                for vals in range(len(isoVary) - 1):
                    # fitparams['del'+str(vals)][i] = fitparams['voigt'+str(vals+1)+'_integral'][i]/fitparams['voigt'+str(vals)+'_integral'][i]
                    # try: fitparams['del'+str(vals)][i] = 1000.0*fitparams['voigt'+str(vals+1)+'_ppmv'][i]/fitparams['voigt'+str(vals)+'_ppmv'][i] - 1000.0
                    try:
                        fitparams["del" + str(vals)][i] = (
                            1000.0
                            * fitparams["voigt" + str(vals + 1) + "_ppmv"][i]
                            / fitparams["voigt" + str(vals) + "_ppmv"][i]
                            - 1000.0
                        )
                    except:
                        fitparams["del" + str(vals)][i] = -9999
                    #logging.debug(fitparams["del" + str(vals)][i])
                    # print(fitparams["del" + str(vals)][i])

            except Exception as e:  # BaseException as e:
                print(e)
                print("error in fitting")
                for key, value in fitparams.items():
                    fitparams[key][i] = -9999

            # ints['newVMR'][i] = -9999
            # continue
            # pass
            # sys.exit(app.exec_())
            # return

        try:
            animationSaveFile = self.basepath.split(".dat")[0] + ".mp4"
            ani = animation.ArtistAnimation(self.figure, ims, interval=20, blit=True)

            Writer = animation.writers["ffmpeg"]
            Writer = animation.FFMpegWriter()
            animation.FFMpegFileWriter
            writer = Writer(fps=50, metadata=dict(artist="Me"), bitrate=1800)
            ani.save(animationSaveFile, writer=writer)
            self.canvas.draw()
        except:
            pass

        """
		with open(self.basepath.split('.dat')[0]+'.csv','w') as outfile:
			#outfile.writelines('Temporary header\r\n')

		headerstring = 'UTC_Start'#, PD, Tdetect, Tlaser, Tcell, Tbody, Tcell2, Pcell, Claser, Vlaser, MFC, AbInt, VMR, Dark, IndexMax'
		if fitparams != -9999:
			hkarray = []
				fitarray = []
				for key, value in HK.items():
					hkarray.append(key)
				for key, value in fitparams.items():
					fitarray.append(key)
				hkarray = np.sort(hkarray)
				fitarray = np.sort(fitarray)
				headerstring+= ', '
				headerstring+= ', '.join(hkarray)
				headerstring+= ', '
				headerstring+= ', '.join(fitarray)
			headerstring+= '\r\n'
			outfile.write(headerstring)

			#daysecs = np.round((HK['juldate']) - gcal2jd('2017','07','01')[0])# - gcal2jd(datestring[0:4],datestring[4:6],datestring[6:8])[1])*86400)
			#daysecs = np.array(daysecs)
			#daysecs = self.seconds
		"""
        # outData = np.c_[daysecs, HK['PD'], HK['tdetect'], HK['tlaser'], HK['temp1'], HK['tbody'], HK['temp2'], HK['press'], HK['current'], HK['vlaser'], HK['MFC'], ints['int'], ints['VMR'], ints['dark'], ints['centerindex']]#, ints['newVMR']]
        # outData = np.c_[self.seconds]

        # for key in hkarray:
        # 	try: outData = np.c_[outData, HK[key]]
        # 	except: pass

        # for key in fitarray:
        # 	try: outData = np.c_[outData, fitparams[key]]
        # 	except: pass#outData = np.c_[outData, HK[key]]

        # for key, value in HK.items():
        # 	outData = np.c_[outData, HK[key]]

        # if fitparams != -9999:
        # for key in fitarray:
        # 	outData = np.c_[outData, fitparams[key]]
        # 	for key, value in fitparams.items():
        # 		outData = np.c_[outData, fitparams[key]]
        # for row in outData:
        # tmp = '{:11d}'.format(int(row[0]))+','
        # row = row[1:]
        # tmp+=','.join(["{:11.6f}".format(x) for x in row])
        # tmp+=','.join(["{:.6E}".format(x) for x in row])
        # tmp+='\r\n'
        # outfile.write(tmp)

        # for i in range(obs):
        # 	scans[i] = scans[i]*HK['normScale'][i]/self.upscale
        # 	bestfits[i] = bestfits[i]*HK['normScale'][i]/self.upscale

        # with open(self.basepath.split('.dat')[0]+'_rawSpectra'+'.csv', 'wb') as csvfile:
        # 	np.savetxt(csvfile, np.arange(-1,1024).reshape(1,np.arange(-1,1024).shape[0]), fmt = '%d', delimiter = ',',  newline = '\r\n')
        # 	np.savetxt(csvfile, np.c_[self.seconds,scans],fmt = '%.6E',delimiter = ',', newline = '\r\n')

        # with open(self.basepath.split('.dat')[0]+'_fitSpectra'+'.csv', 'wb') as csvfile:
        # 	np.savetxt(csvfile, np.arange(-1,1024).reshape(1,np.arange(-1,1024).shape[0]), fmt = '%d', delimiter = ',', newline = '\r\n')
        # 	np.savetxt(csvfile, np.c_[self.seconds,bestfits],fmt = '%.6E',delimiter = ',', newline = '\r\n')

        # out options:
        # best_fit, init_fit, out.residual
        winsound.Beep(1500, 4000)

        if self.pickleSave:
            self.pickleDict["fits"] = fitparams
            with open("./.pickle", "wb") as handle:
                pickle.dump(self.pickleDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return [fitparams, fitparamsDesc]

    def update(self, x, frame):
        self.xdata.append(np.arange(len(frame)))
        self.ydata.append(frame)
        self.ln.set_data(xdata, ydata)
        return (self.ln,)

    def saveText(self, HK, ints, fitparams, outName):
        timestamp = time.strftime("%Y%m%d")
        outName = (
            "".join(outName.split("packaged_")[:-1])
            + "packaged_"
            + str(timestamp)
            + ".csv"
        )
        # datestring = ''.join(''.join(outName.split('CLH2-')[-1:]).split('_')[0])
        datestring = "".join("".join(outName.split("-")[-1:]).split("_")[0])
        dateout = (
            str(datestring[0:4])
            + ", "
            + str(datestring[4:6])
            + ", "
            + str(datestring[6:8])
            + ", "
            + str(timestamp[0:4])
            + ", "
            + str(timestamp[4:6])
            + ", "
            + str(timestamp[6:8])
        )
        self.VMRFileName = outName

        """
		fileNameInfo = './missionInfo.txt'

		outName = os.path.dirname(outName)
		outName += '/'
		with open(fileNameInfo, 'r') as missionRead:
			for i, line in enumerate(missionRead):#line = parFile.readLine()
				line = line.replace(' ','')
				line = line.replace('\n','')
				line = line.replace('\r','')
				line = line.replace('\\','')
				line = line.replace('/','')
				line = line.replace('_','')
				if i < 3:
					if i == 2: outName += str(datestring) + '_'
					outName += line.split(':')[1] + '_'
				else:
					try:
						flightNum = line.split(':')[0]
						flightDate = line.split(':')[1]
						if flightDate == datestring:
							outName += flightNum
							break
					except: outName += 'NA'
			outName += 'Raw'
			outName += '.ict'
		"""

        outName = self.namingConvention(outName, datestring, "Raw")
        self.VMRFileName = outName

        # packagedFileName = './packagedHeader.txt'

        # daysecs = self.seconds
        daysecs = (
            self.HK[0]["juldate"]
            - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[0]
            - gcal2jd((datestring[0:4]), (datestring[4:6]), (datestring[6:8]))[1]
        ) * 86400
        # daysecs = (HK['juldate'] - np.floor(HK['juldate'][0])+0.5)*3600*24#+0.5)*3600*24

        variableNames = []
        variableDesc = []
        for key, value in HK[1].items():
            if key != "juldate":
                variableNames.append(key)
                variableDesc.append(value)

        for key, value in ints[1].items():
            variableNames.append(key)
            variableDesc.append(value)

        try:
            for key, value in fitparams[1].items():
                variableNames.append(key)
                variableDesc.append(value)
            fitparams = fitparams[0]
            for key in fitparams:
                fitparams[key][np.where(fitparams[key] < -999.0)[0]] = -9999

        except:
            pass
    
        HK = HK[0]
        ints = ints[0]
        #fitparams = fitparams[0]

        for key in HK:
            HK[key][np.where(HK[key] < -999.0)[0]] = -9999
        for key in ints:
            ints[key][np.where(ints[key] < -999.0)[0]] = -9999
        outData = np.c_[daysecs]
        # outData = np.c_[daysecs, HK['PD'], HK['tdetect'], HK['tlaser'], HK['temp1'], HK['tbody'], HK['temp2'], HK['press'], HK['current'], HK['vlaser'], HK['MFC'], ints['int'], ints['VMR'], ints['dark'], ints['centerindex']]#, ints['newVMR']]
        for key in HK:
            if key != "juldate":
                outData = np.c_[outData, HK[key]]
        for key in ints:
            outData = np.c_[outData, ints[key]]
        try:
            for key in fitparams:  # variableNames:
                outData = np.c_[outData, fitparams[key]]
                # for key, value in fitparams.items():
                # 	outData = np.c_[outData, value]
        except:
            pass

        self.saveFormat(dateout, outName, outData, variableNames, variableDesc)

        return daysecs

    def namingConvention(self, inputFile="", datestring="", extraComment=""):
        fileNameInfo = "./templates/missionInfo.txt"
        outName = os.path.dirname(inputFile)
        outName += "/"
        with open(fileNameInfo, "r") as missionRead:
            for i, line in enumerate(missionRead):  # line = parFile.readLine()
                line = line.replace(" ", "")
                line = line.replace("\n", "")
                line = line.replace("\r", "")
                line = line.replace("\\", "")
                line = line.replace("/", "")
                line = line.replace("_", "")
                if i < 3:
                    if i == 2:
                        outName += str(datestring) + "_"
                    outName += line.split(":")[1] + "_"
                else:
                    try:
                        flightNum = line.split(":")[0]
                        flightDate = line.split(":")[1]
                        if flightDate == datestring:
                            outName += flightNum
                            break
                    except:
                        outName += "NA"
            outName += extraComment
            outName += ".ict"

        return outName
        # self.VMRFileName = outName

    def saveFormat(
        self,
        dateout="",
        outName="",
        outData=[],
        variableNames=[],
        variableDesc=[],
        variableUnits=[],
    ):
        packagedFileName = "./templates/headerFormat.txt"

        if variableUnits == []:
            variableUnits = ["unit"] * len(variableNames)

        ###Write header:::
        header = []
        counter = 0
        with open(outName, "w", newline="") as outFile:
            with open(packagedFileName, "r") as headerFile:
                for i, line in enumerate(headerFile):  # line = parFile.readLine()
                    try:
                        line = line.replace("\n", "")
                        line = line.replace("\r", "")
                        if i <= 15:
                            line = ":".join(line.split(":")[1:])
                            line = line.lstrip()
                            if len(line) == 0:
                                continue
                            if i == 6:
                                counter += 1
                                header.append([dateout])
                            if i == 9 or i == 10:
                                line = [line] * len(variableNames)
                                header.append([", ".join(line)])
                                continue
                            if i == 11:
                                for var in zip(
                                    variableNames, variableUnits, variableDesc
                                ):
                                    header.append(
                                        [var[0] + ", " + var[1] + ", " + var[2]]
                                    )
                                    counter += 1
                                continue
                        header.append([line])
                    except:
                        pass

            header.append([", ".join(["Start_UTC"] + variableNames)])

            header[0][0] = str(int(len(header))) + ", " + header[0][0]

            header[9][0] = str(int(len(variableNames)))

            header[12 + counter][0] = str(int(len(header[13 + counter :])))

            for line in header:
                outFile.write(line[0])
                outFile.write("\n")

            for row in outData:
                # tmp = '{:11d}'.format(int(row[0]))+','
                tmp = "{:.3f}".format((row[0])) + ","
                row = row[1:]
                # tmp+=','.join(["{:11.6f}".format(x) for x in row])
                tmp += ",".join(["{:.6e}".format(x) for x in row])
                tmp += "\n"
                outFile.write(tmp)

        # icartt file name is of the following format:
        # 	dataID_locationID_YYYYMMDD[hh[mm[ss]]]_R#[_L#][_V#][_comments].ict
        # example:
        # 	ORCAS-CUTOTAL-H2O_GV_2018MMDD_R1_FF01.ict

        # icart required headers from format file.

        return header

    def plotResults(self, HK, SC, ints, outName="", figSelect=-1):
        # plt.figure(1)

        datestring = self.startTime.text()[0:8]
        print(datestring)
        CLHtime = np.round(
            (
                HK["juldate"]
                - gcal2jd(datestring[0:4], datestring[4:6], datestring[6:8])[0]
                - gcal2jd(datestring[0:4], datestring[4:6], datestring[6:8])[1]
            )
            * 86400
        )
        CLHtime = np.array(CLHtime)

        timestamp = time.strftime("%Y%m%d")
        try:
            outName = (
                "".join(outName.split("plot_")[:-1]) + "plot_" + str(timestamp) + ".png"
            )
        except:
            pass
        # datestring = ''.join(''.join(outName.split('CLH2-')[-1:]).split('_')[0])
        # dateout = str(datestring[0:4])+', '+str(datestring[4:6])+', '+str(datestring[6:8])+', '+str(timestamp[0:4])+', '+str(timestamp[4:6])+', '+str(timestamp[6:8])

        # self.setWindowState(QtCore.Qt.WindowMaximized)
        # app.processEvents()

        # for i in range(1,2):

        if figSelect == -1:
            figure = plt.figure(figsize=(12, 6))

            figure.clear()

            # fig, ax = self.figure.add_subplot(231)
            ax = figure.add_subplot(231)
            ax.plot(CLHtime, ints["VMR"], "k")
            ax.set_title("VMR observation")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("VMR (ppmv)")

            ax = figure.add_subplot(232)
            ax.plot(
                CLHtime,
                HK["temp1"],
                "k",
                CLHtime,
                HK["temp2"],
                "r",
                CLHtime,
                HK["tbody"],
                "b",
            )
            ax.set_title("Cell (bk, r) and body (blu) temps")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Temperature (degC)")

            ax = figure.add_subplot(233)
            ax.plot(CLHtime, HK["press"], "k")
            ax.set_title("Pressure")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Pressure (mb)")

            ax = figure.add_subplot(234)
            ax.plot(CLHtime, HK["MFC"], "k")
            ax.set_title("Mass flow rate")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("MFC (sLm)")

            ax = figure.add_subplot(235)
            ax.plot(CLHtime, HK["tlaser"], "r", CLHtime, HK["tdetect"], "k")
            ax.set_title("Laser (r) and Detector (bk) Temp")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Temperature (raw voltage)")

            ax = figure.add_subplot(236)
            ax.plot(
                np.arange(len(SC["scans"][0, :])),
                SC["scans"][round(len(ints["VMR"]) / 2), :],
                "k",
            )
            ax.set_title("Sample scan")
            ax.set_xlabel("sample")
            ax.set_ylabel("Scan Units (cts)")

            # ax.set_subplots_adjust(top=0.92, bottom=0.08, left = 0.10, right = 0.95, hspace = 0.25, wspace = 0.35)

            figure.tight_layout(pad=0, w_pad=0, h_pad=0)

            figure.savefig(outName)

            # Set to redraw canvas on resizing
            # Need to save figure in raw form

        figure = self.figure
        figure.clear()
        ax = figure.add_subplot(111)
        if figSelect <= 0:
            ax.plot(CLHtime, ints["VMR"], "k")
            ax.set_title("VMR observation")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("VMR (ppmv)")
        elif figSelect == 1:
            ax.plot(
                CLHtime,
                HK["temp1"],
                "k",
                CLHtime,
                HK["temp2"],
                "r",
                CLHtime,
                HK["tbody"],
                "b",
            )
            ax.set_title("Cell (bk, r) and body (blu) temps")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Temperature (degC)")
        elif figSelect == 2:
            ax.plot(CLHtime, HK["press"], "k")
            ax.set_title("Pressure")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Pressure (mb)")
        elif figSelect == 3:
            ax.plot(CLHtime, HK["MFC"], "k")
            ax.set_title("Mass flow rate")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("MFC (sLm)")
        elif figSelect == 4:
            ax.plot(CLHtime, HK["tlaser"], "r", CLHtime, HK["tdetect"], "k")
            ax.set_title("Laser (r) and Detector (bk) Temp")
            ax.set_xlabel("Seconds")
            ax.set_ylabel("Temperature (raw voltage)")
        elif figSelect == 5:
            ax.plot(
                np.arange(len(SC["scans"][0, :])),
                SC["scans"][round(len(ints["VMR"]) / 2), :],
                "k",
            )
            ax.set_title("Sample scan")
            ax.set_xlabel("sample")
            ax.set_ylabel("Scan Units (cts)")

        self.figMenu.setVisible(True)

        self.canvas.draw()
        app.processEvents()
        # plt.show()
        # plt.plot(np.arange(numSC), SC['scans'][0,:])#)#[:,0])
        # plt.show()

        # self.setWindowState(QtCore.Qt.WindowNoState)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Python Files (*.py)", options = options)
        # files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "/mnt/c/Users/rainw/Desktop/github/CLH2/python/Test/", "All Files (*);;Python Files (*.py)", options = options)
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "./",
            "HK and SC Files (*HK*;*SC*);;All Files (*)",
            options=options,
        )
        # 	print(files)
        if files:
            return files
        else:
            return False

    # def loadHitranKeys(self):
    # 	fileName = './hitranKeys.csv'
    # 	with open(fileName, mode = 'r') as infile:
    # 		reader = csv.reader(infile)
    # 		self.masterHitranKeys = {rows[0]+' '+rows[1]: rows[:] for rows in reader}

    #

    """
	def readHitran(self, masterHitranKeys, lines=[], cutoffOrder = 1e10, magCutoffSlope = 5.0):
		#Read the reduced hitran file containing subset to minimize process time. May use full file but beware of memory.

		db_begin(data)
		#fetch('H2O',1,1,min(x),max(x))
		fetch_by_ids('H2O',[1,2,3,4],10000000.0/wvMax, 10000000.0/wvMin,)

		#print((hitran[0,:]))
		select('H2O')
		numLines = (len(getColumn('H2O','nu')))

		#for col in
		hitranHeaders = ['MI','nu','S','A','gair','gsel','E_nair','dair']

		hitranArr = np.zeros(numLines, dtype = 'float')
		for key in hitranHeaders:
			hitranArr = np.c_[hitranArr, getColumn('H2O',key)]
		return

		wd = './'
		with open(wd + '1365-1395.csv','r') as csvFile:#01_hit16.par','r') as csvFile:
			spamreader = csv.reader(csvFile, delimiter = ',')
			for i, row in enumerate(spamreader):
				#print(row)
				if i == 0: continue
				try: tmprow = np.array([float(x) for x in row])
				except: continue
				try: hitranArr = np.c_[hitranArr, tmprow]
				except: hitranArr = np.c_[tmprow]

		#used to remove the duplicate starter lines used for estimating window size
		numlines = len(hitranArr[0,:])

		#Load hitran data file.
		hitranArr = np.transpose(hitranArr)

		#Precondition parameter matrix
		molMass = np.zeros(len(hitranArr[:,0]), dtype = 'float')#self.hitranPars[:,0]))

		# This number should correspond to an array with isotopes that are allowed to float along an "adjusted ppmv".
		# If the iso number is not in the list, it is asserted to the primary isotope (11)
		isoVary = np.unique(hitranArr[:,1])#self.hitranPars[:,1])
		isoVary = np.sort(isoVary)

		#if len(isoVary) > 2: isoVary = isoVary[:2]
		#if len(isoVary) > 1: isoVary = isoVary[:1]

		#Configure mixing ratios associated with individual isotopes
		ppmvNum = np.zeros(len(molMass),dtype = 'int')
		for isoInc, iso in enumerate(isoVary):
			if iso in hitranArr[:,1]:
				ppmvNum[np.where(hitranArr[:,1] == iso)] = isoInc
				#ppmvNum[hitranArr[:,1] == iso] = isoInc

		#Configure hitran parameters array
		hitranTable = np.c_[molMass]
		for i in range(0,10): hitranTable = np.c_[hitranTable, hitranArr[:,i]]
		hitranTable = np.c_[hitranTable, ppmvNum]

		for i in range(len(hitranTable[:,0])):
			hitranTable[i,0] = masterHitranKeys[str(int(hitranTable[i,1]))+' '+str(int(hitranTable[i,2]))][9]

		#Now filter the table based on cushion and roll off filter

		#Find center of window
		windowCenter = (max(lines) - min(lines))/2.0 + min(lines)
		#Double window as the official range!
		windowHW = np.abs(max(lines)-min(lines))/2.0
		#print(max(lines), min(lines))

		#Find the maximum intensity line within the window
		windowMax = np.max(hitranTable[(hitranTable[:,3]>(windowCenter - windowHW))\
			*(hitranTable[:,3] < (windowCenter + windowHW)),4])
		#use cushion to determine what the minimum perceivable lines in window are
		windowMin = windowMax/cutoffOrder
		#windowMin = cushion#5e15

		mask = np.ones(numlines)

		for i in range(numlines):
			#if hitranTable[i,3] < min(lines),
			#Check distance of line to center of window
			distance = np.abs(hitranTable[i,3] - windowCenter)
			#If distance within allowable range, make sure greater than minimum
			if distance < windowHW:
				if hitranTable[i,4] < windowMin:
					mask[i] = 0
			else:
				mask[i] = 0
				#If outside of window, use rolloff slope based on # of window HW's
				#   outside of range. Allowable minimum increases further from window
				if hitranTable[i,4] < (np.abs(distance - windowHW)/(windowHW))*magCutoffSlope*(windowMin):
					mask[i] = 0

		hitranTable = hitranTable[np.where(mask)[0], :]
		numlines = len(hitranTable[:,0])#wavelength)

		return hitranTable
	"""

    def hitranIDChange(self, edited=False):
        # self.molMenu.clear()
        # self.isoMenu.clear()
        self.molMenu.blockSignals(True)
        self.isoMenu.blockSignals(True)
        self.hitranVMR.blockSignals(True)
        self.hitranFrac.blockSignals(True)

        try:
            mol = str(int(self.molMenu.currentText()[:2]))
        except:
            mol = -1  # self.molMenu.currentText()
        try:
            iso = str(int(self.isoMenu.currentText()[:2]))
        except:
            iso = -1  # self.isoMenu.currentText()

        # print(mol, iso)

        # try: print(int(self.molMenu.currentText()[:2]))
        # except: print('failed')

        if not edited:
            if self.molMenu.currentIndex() == 0:
                self.isoMenu.clear()
                self.hitranVMR.setValue(0)
                self.hitranFrac.setValue(0)
                self.hitranVMR.setDisabled(True)
                self.hitranFrac.setDisabled(True)
            else:
                if self.isoMenu.count() == 0:  # or self.isoMenu.currentIndex() == 0:
                    self.hitranFrac.setValue(0)
                    self.isoMenu.addItem("Mixed")
                    uniqueIso = np.unique(
                        self.slaveHitranKeys[
                            np.where(self.slaveHitranKeys[:, 0] == mol)[0], 1
                        ]
                    )
                    labels = []
                    for labelIso in uniqueIso:
                        # labels.append(self.masterHitranKeys[mol+' '+labelIso][4])
                        labels.append(
                            self.molecularInfoDict[mol + "_" + labelIso]["formula"]
                        )
                    self.isoMenu.addItems(
                        [x + " -- " + y for x, y in zip(uniqueIso, labels)]
                    )

                # if self.isoMenu.currentIndex() == 0 or int(iso) <= 1:
                if self.isoMenu.currentIndex() == 0 or int(iso) == 1 or int(iso) == -1:
                    self.hitranFrac.setDisabled(True)
                    self.hitranVMR.setDisabled(False)
                    self.hitranFrac.setValue(0)
                else:
                    self.hitranFrac.setDisabled(False)
                    # self.hitranVMR.setDisabled(True)
                    try:
                        # self.hitranFrac.setValue(float(self.masterHitranKeys[mol+' '+iso][8]))
                        self.hitranFrac.setValue(
                            float(self.molecularInfoDict[mol + "_" + iso]["dummy"])
                        )
                    except:
                        self.hitranFrac.setValue(0)

                try:
                    # self.hitranVMR.setValue(float(self.masterHitranKeys[mol+' 1'][7]))
                    self.hitranVMR.setValue(
                        float(self.molecularInfoDict[mol + "_1"]["conc"])
                    )
                except:
                    self.hitranVMR.setValue(0)
        else:
            try:
                # if int(iso) == 1 or int(iso) == -1:
                if self.molMenu.currentIndex() != 0:  # self.isoMenu.currentIndex() == 0:
                    # self.masterHitranKeys[mol+' 1'][7] = str(self.hitranVMR.value())
                    self.molecularInfoDict[mol + "_1"]["conc"] = str(
                        self.hitranVMR.value()
                    )
                if (
                    int(iso) != -1
                    and int(iso) != 1
                    and self.molMenu.currentIndex() != 0
                    and self.isoMenu.currentIndex() != 0
                    and int(iso) > 1
                ):
                    # self.masterHitranKeys[mol+' '+iso][8] = str(self.hitranFrac.value())
                    self.molecularInfoDict[mol + "_" + iso]["dummy"] = str(
                        self.hitranFrac.value()
                    )
                    # self.masterHitranKeys[mol+' 1'][7] = str(self.hitranVMR.value())
                    self.molecularInfoDict[mol + "_1"]["conc"] = str(
                        self.hitranVMR.value()
                    )
            except:
                pass

        self.molMenu.blockSignals(False)
        self.isoMenu.blockSignals(False)
        self.hitranVMR.blockSignals(False)
        self.hitranFrac.blockSignals(False)

        # self.molMenu.addItem('Mixed')
        # self.molMenu.addItems([str(x) for x in np.unique(self.hitranPars[:,0])])
        # self.molMenu.addItems([str(x) for x in np.unique(self.hitranPars[:,0])])
        # self.isoMenu.addItem('Mixed')

    def plotHitran(self):
        # def spectralModel(self, pars, x, hitran, raw = False, prefix = None, data = None):
        self.hitranFigure.clear()
        ax = self.hitranFigure.add_subplot(111)

        # Are we plotting line intensities, cross sec, abs, trans?
        # For now assume trans

        # create isotope variation array and inject into parameter array
        molMass = np.zeros(len(self.hitranPars[:, 0]), dtype="float")
        # for i in range(len(self.hitranPars[:,0])):
        # 	if self.hitranPars[i,1] == 1: molMass[i] = 16
        # 	elif self.hitranPars[i,1] == 2: molMass[i] = 18
        # 	else: molMass[i] = 17

        # Number of isotopes to allow to vary....
        # This number should correspond to an array with isotopes that are allowed to float along an "adjusted ppmv".
        # If the iso number is not in the list, it is asserted to the primary isotope (11)
        # isoVary = [11]
        ppmvNum = np.zeros(len(molMass), dtype="float")

        # order of hitranPars is:
        # 	molMass, wavelength, intensity, einsteinA, airWidth,
        # 	selfWidth, lowerStateEnergy, tempDep, pressShift
        hitranPars = np.c_[molMass]
        for i in range(0, 10):
            hitranPars = np.c_[hitranPars, self.hitranPars[:, i]]
        hitranPars = np.c_[hitranPars, ppmvNum]
        # hitranPars = np.c_[molMass, self.hitranPars[:,2], self.hitranPars[:,3], self.hitranPars[:,4], airWidth, \
        # 	selfWidth, lowerStateEnergy, tempDep, pressShift, ppmvNum]

        pars = Parameters()
        pars.add("press", value=self.hitranPress.value())
        pars.add("temp", value=self.hitranTemp.value())
        pars.add("path", value=self.hitranPath.value())
        # for i in range(len(isoVary)):

        # Section for reducing the dataset for plotting only certain lines
        if self.molMenu.currentIndex() != 0:
            hitranPars = hitranPars[
                np.where(hitranPars[:, 1] == int(self.molMenu.currentText()[:2]))
            ]
            if self.isoMenu.currentIndex() != 0:
                hitranPars = hitranPars[
                    np.where(hitranPars[:, 2] == int(self.isoMenu.currentText()[:2]))
                ]

        isoInc = 0
        uniqueMols = np.unique(hitranPars[:, 1])
        for mol in uniqueMols:
            if mol in uniqueMols:
                uniqueIsos = np.unique(
                    self.hitranPars[np.where(self.hitranPars[:, 0] == mol)[0], 1]
                )
                for iso in uniqueIsos:
                    if iso in hitranPars[:, 2]:
                        # ppmvNum[np.where(self.hitranPars[:,1] == iso)] = isoInc
                        hitranPars[
                            np.where(
                                np.logical_and(
                                    hitranPars[:, 2] == iso, hitranPars[:, 1] == mol
                                )
                            )[0],
                            11,
                        ] = isoInc
                        if iso == 1:
                            # pars.add('voigt'+str(isoInc)+'_ppmv', value = float(self.masterHitranKeys[str(int(mol))+' '+str(int(iso))][7]))
                            pars.add(
                                "voigt" + str(isoInc) + "_ppmv",
                                value=float(
                                    self.molecularInfoDict[
                                        str(int(mol)) + "_" + str(int(iso))
                                    ]["conc"]
                                ),
                            )
                        else:
                            # Fractionation is ((weak/strong)/(expected) - 1)*1000
                            # pars.add('voigt'+str(isoInc)+'_ppmv', value = float(self.masterHitranKeys[str(int(mol))+' 1'][7]) * \
                            pars.add(
                                "voigt" + str(isoInc) + "_ppmv",
                                value=float(
                                    self.molecularInfoDict[str(int(mol)) + "_1"]["conc"]
                                )
                                * (
                                    1
                                    + float(
                                        self.molecularInfoDict[
                                            str(int(mol)) + "_" + str(int(iso))
                                        ]["dummy"]
                                    )
                                    / 1000.0
                                ),
                            )
                            # 	(1 + float(self.masterHitranKeys[str(int(mol))+' '+str(int(iso))][8])/1000.0))
                        isoInc += 1

        # for i in range(len(np.unique(ppmvNum))):
        # 	pars.add('voigt'+str(i)+'_ppmv', value = self.hitranVMR.value())#100.0)#, vary = False)

        # def spectralModel(self, pars, x, hitran, raw = False, prefix = None, data = None):
        # print(self.hitranDomain)
        # spectra = self.spectralModel(pars,10000000.0/self.hitranDomain,hitranPars,raw=True)
        spectra = spectralWrapper(
            pars, 10000000.0 / self.hitranDomain, hitran, molecularInfoDict, raw=True
        )

        # print(self.hitranDomain)

        line1, = ax.plot(
            self.hitranDomain, spectra, "b"
        )  # ,testDom,DPL_VMR,'k',testDom,DPR_VMR,'r')#timestamp,vmr,'r')

        linePeakDomain = hitranPars[:, 3]
        # peakValues = self.spectralModel(pars, linePeakDomain, hitranPars, raw = True)
        peakValues = spectralWrapper(
            pars, linePeakDomain, hitran, molecularInfoDict, raw=True
        )
        # print(linePeakDomain, peakValues)

        ax2 = ax.twinx()

        # Filter Out very small lines

        uniqueMol = np.unique(hitranPars[:, 1])
        uniqueIso = np.unique(hitranPars[:, 2])
        molColorIndex = 0
        isoColorIndex = 0
        # print(cm.rainbow(100))
        # colorArr = cm.rainbow(np.linspace(0,1,len(uniqueMol)*len(uniqueIso)))
        colorArr = cm.rainbow(np.linspace(0, 1, max(len(uniqueMol), len(uniqueIso))))
        # colorArr = ['b','r','y','c']
        for mol in uniqueMol:
            for iso in uniqueIso:
                print(str(int(mol)) + str(int(iso)))
                # redIndices = np.where(np.logical_and(hitranPars[:,1] == mol, hitranPars[:,2] == iso,2\
                # 	10000000.0/hitranPars[:,3] < self.hitranMax.value(), 10000000.0/hitranPars[:,3] > self.hitranMin.value()))[0]
                redIndices = np.where(
                    (hitranPars[:, 1] == mol)
                    & (hitranPars[:, 2] == iso)
                    & (10000000.0 / hitranPars[:, 3] < self.hitranMax.value())
                    & (10000000.0 / hitranPars[:, 3] > self.hitranMin.value())
                )[0]
                try:
                    # spectra = self.spectralModel(pars,10000000.0/self.hitranDomain,hitranPars,raw=True)
                    # markerlines, stemlines, baseline = ax2.stem(10000000.0/hitranPars[redIndices,3], hitranPars[redIndices,4],\
                    # 	label = str(int(mol))+str(int(iso)), markerfmt = 'b.' ,basefmt = ' ')#, bottom = 1e-80)
                    # print(self.spectralModel(pars, hitranPars[redIndices,3], hitranPars[redIndices, :]))
                    # print(self.spectralModel(pars, hitranPars[redIndices,3], hitranPars[redIndices, :], raw = True))
                    markerlines, stemlines, baseline = ax2.stem(
                        10000000.0 / hitranPars[redIndices, 3],
                        self.spectralModel(
                            pars, hitranPars[redIndices, 3], hitranPars[:, :], raw=True
                        ),
                        label=str(int(mol)) + str(int(iso)),
                        markerfmt="b.",
                        basefmt=" ",
                        bottom=1.0,
                    )
                    plt.setp(stemlines, color=colorArr[isoColorIndex], linestyle="--")
                    plt.setp(markerlines, color=colorArr[molColorIndex])

                    # labels = [self.masterHitranKeys[str(int(mol))+' '+str(int(iso))][4]]*len(hitranPars[redIndices,3])
                    labels = [
                        self.molecularInfoDict[str(int(mol)) + "_" + str(int(iso))][
                            "formula"
                        ]
                    ] * len(hitranPars[redIndices, 3])
                    # labels = labels + ': ' + '{:3E}'.format(self.hitranPars[redIndices,4])
                    labels = [
                        x + ": \n" + y
                        for x, y in zip(
                            labels,
                            ["{:.2E}".format(x) for x in hitranPars[redIndices, 4]],
                        )
                    ]

                    # self.molMenu.addItems([x + ' -- ' + y for x,y in zip(uniqueMols,labels)])

                    xRange = max(self.hitranDomain) - min(self.hitranDomain)
                    yRange = max(spectra) - min(spectra)

                    # slopes = (np.roll(spectra, -1)[1:-1]-spectra[1:-1])/(np.roll(self.hitranDomain[1:-1], -1)[:]-self.hitranDomain[1:-1])
                    slopes = np.gradient(spectra)
                    slopes /= self.hitranDomain[1] - self.hitranDomain[0]
                    # slopes /= np.abs(yRange)

                    # slopes = np.interp(10000000.0/hitranPars[redIndices,3], np.arange(len(slopes)), slopes)
                    slopes = np.interp(
                        10000000.0 / hitranPars[redIndices, 3], self.hitranDomain, slopes
                    )
                    # slopes /= np.abs(yRange)
                    # slopes *= np.abs(xRange)

                    # slopes *= len(slopes)

                    slopes *= np.pi
                    slopes -= np.pi / 2

                    print(10000000.0 / hitranPars[redIndices, 3])
                    print(slopes)
                    # slopes += np.pi

                    # for x, y, label in zip(10000000.0/hitranPars[redIndices,3], hitranPars[redIndices,4], labels):
                    for slope, x, y, label in zip(
                        slopes,
                        10000000.0 / hitranPars[redIndices, 3],
                        self.spectralModel(
                            pars, hitranPars[redIndices, 3], hitranPars[:, :], raw=True
                        ),
                        labels,
                    ):
                        angleX = np.cos(slope)
                        angleY = np.sin(slope)
                        # ax2.annotate(label, xy = (x,y), xytext = (angleX*30, -np.abs(angleY*30)), \
                        # 	textcoords = 'offset points', ha = 'center', va = 'center', \
                        # 	bbox = dict(boxstyle = 'round,pad=0.2', fc = 'lightblue', alpha = 0.5),\
                        # 	arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

                    isoColorIndex += 1
                except:
                    pass  # print('Failed stem plot')
            molColorIndex += 1

        ax2.legend()
        # validDomain = np.where(hitranPars[:,1]
        # markerlines, stemlines, baseline = ax2.stem(hitranPars[:,1], hitranPars[:,2])#,'.')#peakValues, '.')
        # ax2.setp(stemlines, 'color', ax2.getp(markerline, 'color'))
        # ax2.setp(stemlines, 'linestyle', 'dotted')

        # ax2.invert_yaxis()

        # ax2.set_yscale('log')

        # with open('./hi'+'.csv', 'wb') as csvfile:
        # np.savetxt(csvfile, np.c_[seconds+microseconds*1e-6,HKdata],fmt = '%.6f',delimiter = ',', newline = '\r\n', header = 'seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC')
        # 	np.savetxt(csvfile, np.c_[10000000.0/self.hitranDomain, spectra],fmt = '%6e',delimiter = ',', newline = '\r\n', header = 'seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC')

        ax.relim()
        ax.autoscale()
        ax2.relim()
        ax.autoscale()

        self.hitranFigure.subplots_adjust(left=0.05, right=0.95, bottom=0.07, top=0.92)
        ax.axis("tight")
        ax2.axis("tight")

        self.hitranCanvas.draw()
        app.processEvents()

    def loadHitran(self, uniqueFile=False):
        loadHitranKeys()
        if uniqueFile:
            # self.hitranFile = self.openFileNamesDialog()
            options = QFileDialog.Options()
            self.hitranFile, _ = QFileDialog.getOpenFileName(
                self,
                "Select HITRAN file",
                "./",
                "Hitran file (*.par);;All Files (*)",
                options=options,
            )

            # if self.hitranFile: return
        # self.hitranFile = './100nm-10um-HITRAN.par'
        else:
            self.hitranFile = "./01_hit12.par"
        # Begin Parsing .par hitran file

    def processHitran(self):
        # try:
        # self.hitranPars = []
        charLen = [0, 2, 1, 12, 10, 10, 5, 5, 10, 4, 8]  # ,15,15,15,15,6,12,1,7]
        # self.hitranPars = []
        firstPass = True
        if self.wavelengthOption.isChecked():
            low = min(
                10000000.0 / self.hitranMin.value(), 10000000.0 / self.hitranMax.value()
            )
            high = max(
                10000000.0 / self.hitranMin.value(), 10000000.0 / self.hitranMax.value()
            )
        else:
            low = min(self.hitranMin.value(), self.hitranMax.value())
            high = max(self.hitranMin.value(), self.hitranMax.value())
        self.hitranDomain = np.arange(
            10000000.0 / high, 10000000.0 / low, self.hitranRes.value()
        )  # (high-low)/10000)
        # self.hitranDomain = 10000000.0/self.hitranDomain
        # print(self.hitranDomain)
        low -= self.hitranCush.value()
        high += self.hitranCush.value()

        with open(self.hitranFile, "r") as parFile:
            for line in parFile:  # line = parFile.readLine()
                lineParse = []
                testPar = float(line[np.sum(charLen[:3]) : np.sum(charLen[:4])])

                if testPar < low or testPar > high:
                    continue
                for parCntr in range(len(charLen)):
                    try:
                        lineParse.append(
                            float(
                                line[
                                    np.sum(charLen[:parCntr]) : np.sum(
                                        charLen[: parCntr + 1]
                                    )
                                ]
                            )
                        )
                    except:
                        pass
                # self.hitranPars.append(lineParse)
                if firstPass:
                    self.hitranPars = np.c_[lineParse]
                    firstPass = False
                else:
                    try:
                        self.hitranPars = np.c_[self.hitranPars, (lineParse)]
                    except:
                        pass
        self.hitranPars = np.transpose(self.hitranPars)
        # self.hitranPars = np.array(self.hitranPars)

        self.slaveHitranKeys = []
        try:
            uniqueMols = np.sort(np.unique(self.hitranPars[:, 0]))
        except:
            uniqueMols = np.unique(self.hitranPars[:, 0])
        for mol in uniqueMols:
            try:
                uniqueIsos = np.sort(
                    np.unique(self.hitranPars[np.where(self.hitranPars[:, 0] == mol), 1])
                )
            except:
                uniqueIsos = np.unique(
                    self.hitranPars[np.where(self.hitranPars[:, 0] == mol), 1]
                )
            for iso in uniqueIsos:
                try:
                    self.slaveHitranKeys.append(
                        [str(int(mol)), str(int(iso)), 0.00]
                    )  # , self.masterHitranKeys[str(int(mol))+' '+str(int(iso))][7],\
                    # 	self.masterHitranKeys[str(int(mol))+' '+str(int(iso))][8]])
                except:
                    pass
        self.slaveHitranKeys = np.array(self.slaveHitranKeys)

        self.molMenu.clear()
        self.isoMenu.clear()

        self.molMenu.addItem("Mixed")
        labels = []
        uniqueMols = np.unique(self.slaveHitranKeys[:, 0])  # .sort()
        for mol in uniqueMols:  # uniqueMols:
            # labels.append(self.masterHitranKeys[mol+' 1'][2])#+ ' - ' + self.masterHitranKeys[mol+ ' 1'][3])
            labels.append(
                self.molecularInfoDict[mol + "_1"]["molecule"]
            )  # + ' - ' + self.molecularInfoDict[mol+ ' 1'][3])
        # self.molMenu.addItems([str(x) for x in np.unique(self.hitranPars[:,0])])
        self.molMenu.addItems([x + " -- " + y for x, y in zip(uniqueMols, labels)])
        # self.isoMenu.addItem('Mixed')
        # self.isoMenu.addItems([str(x) for x in np.unique(self.hitranPars[:,1])])

        # print(self.hitranPars)
        self.plotHitranButton.setDisabled(False)

        # except: return

    # def modelHitran(self):
    def hitranDomainSwap(self, option=0):
        # return
        if option == 0:
            return
        if option == 1:  # self.wavelengthOption.isChecked():
            self.hitranDomainLabel.setText("Wavelength Domain (nm)")
            self.hitranMinLabel.setText("Minimum (nm)")
            self.hitranMaxLabel.setText("Maximum (nm)")
            self.hitranResLabel.setText("Resolution (nm)")
            self.hitranCushLabel.setText("Window Excess (nm)")
            # if self.wavenumberOption.isChecked():
            tmp = self.hitranMin.value()
            resSteps = (
                self.hitranMax.value() - self.hitranMin.value()
            ) / self.hitranRes.value()
            res = self.hitranRes.value() / (
                10000000 / ((self.hitranMin.value() + self.hitranMax.value()) / 2) ** 2
            )
            excess = self.hitranCush.value() / (
                10000000 / ((self.hitranMin.value() + self.hitranMax.value()) / 2) ** 2
            )
            self.hitranMin.setValue(10000000.0 / self.hitranMax.value())
            self.hitranMax.setValue(10000000.0 / tmp)
            self.hitranRes.setValue(
                (self.hitranMax.value() - self.hitranMin.value()) / resSteps
            )
            self.hitranCush.setValue(
                np.abs(
                    10000000.0
                    / (10000000.0 / self.hitranMin.value() - self.hitranCush.value())
                    - self.hitranMin.value()
                )
            )
            self.wavenumberOption.setDisabled(False)
            self.wavelengthOption.setDisabled(True)
        else:
            self.hitranDomainLabel.setText("Wavenumber Domain (cm-1)")
            self.hitranMinLabel.setText("Minimum (cm-1)")
            self.hitranMaxLabel.setText("Maximum (cm-1)")
            self.hitranResLabel.setText("Resolution (cm-1)")
            self.hitranCushLabel.setText("Window Excess (cm-1)")
            # if self.wavelengthOption.isChecked():
            tmp = self.hitranMin.value()
            resSteps = (
                self.hitranMax.value() - self.hitranMin.value()
            ) / self.hitranRes.value()
            res = self.hitranRes.value() / (
                10000000 / ((self.hitranMin.value() + self.hitranMax.value()) / 2) ** 2
            )
            excess = self.hitranCush.value() / (
                10000000 / ((self.hitranMin.value() + self.hitranMax.value()) / 2) ** 2
            )
            self.hitranMin.setValue(10000000.0 / self.hitranMax.value())
            self.hitranMax.setValue(10000000.0 / tmp)
            self.hitranRes.setValue(
                (self.hitranMax.value() - self.hitranMin.value()) / resSteps
            )
            self.hitranCush.setValue(
                np.abs(
                    10000000.0
                    / (10000000.0 / self.hitranMax.value() + self.hitranCush.value())
                    - self.hitranMax.value()
                )
            )
            # self.hitranCush.setValue(excess)
            self.wavelengthOption.setDisabled(False)
            self.wavenumberOption.setDisabled(True)

    def resetHitranAbundances(self):
        print("hi")

    def closeEvent(self, event):
        result = QMessageBox.warning(
            MainWindow,
            "WARNING",
            "Are you sure you want to close the program?",
            QMessageBox.Yes,
            QMessageBox.No,
        )
        event.ignore()

        if result == QMessageBox.Yes:
            self.closeTrigger = True
            event.accept()
            
    def workerVariableHold(self, var):
        self.threadVar = var

#### CODE TAKEN FROM https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/ ###
''' 
    worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
    worker.signals.result.connect(self.print_output)
    worker.signals.finished.connect(self.thread_complete)

    # Execute
    self.threadpool.start(worker) 
'''
class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
            
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
            
            

# Currently Unused
class QServer(QThread):
    def __init__(self, variable, parent=None):
        super(QServer, self).__init__(parent)
        self.variable = variable

    def run(self):
        variable = self.variable
        # DO STUFFS

    # def stop(self):
    # Stuff to do when ready to stop
    def __del__(self):
        self.quit()
        self.wait()


if __name__ == "__main__":
    # app = QtWidgets.QApplication(sys.argv)
    # MainWindow = MyWindow()
    # ui = Ui_MainWindow()
    # ui.initUI(MainWindow)
    # MainWindow.showMaximized()
    # sys.exit(app.exec_())

    app = QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.setWindowTitle("CLH2 Extraction Program")

    # MainWindow.setGeometry(MainWindow.left, MainWindow.top, MainWindow.width, MainWindow.height)
    MainWindow.show()  # Maximized()
    # MainWindow.setWindowState(QtCore.Qt.WindowMaximized)
    # app.processEvents()

    sys.exit(app.exec_())
