from common.libraryImports import *


def initUI(self):
    self.setWindowTitle(self.title)
    #self.setGeometry(self.left, self.top, self.width, self.height)

    self.centralWidget = QtWidgets.QWidget()
    self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)

    self.tabWidget = QtWidgets.QTabWidget(self.centralWidget)
    self.tabWidget.setStyleSheet("""QTabWidget{background-color: rgb(220,220,255);}""")

    self.tab1 = QtWidgets.QWidget()
    self.tabWidget.addTab(self.tab1, "Operation")

    self.tab2 = QtWidgets.QWidget()
    self.tabWidget.addTab(self.tab2, "Configuration")

    self.tab3 = QtWidgets.QWidget()
    self.tabWidget.addTab(self.tab3, "HITRAN")

    self.tabLayout1 = QtWidgets.QGridLayout(self.tab1)
    self.tabLayout1.setContentsMargins(10, 10, 10, 10)
    self.tabLayout1.setSpacing(5)

    self.tabLayout2 = QtWidgets.QGridLayout(self.tab2)
    self.tabLayout2.setContentsMargins(10, 10, 10, 10)
    self.tabLayout2.setSpacing(5)

    self.tabLayout3 = QtWidgets.QGridLayout(self.tab3)
    self.tabLayout3.setContentsMargins(10, 10, 10, 10)
    self.tabLayout3.setSpacing(5)

    for i in range(0, 100):
        self.tabLayout1.setColumnMinimumWidth(i, 1)
        self.tabLayout1.setColumnStretch(i, 1)
        self.tabLayout2.setColumnMinimumWidth(i, 1)
        self.tabLayout2.setColumnStretch(i, 1)
        self.tabLayout3.setColumnMinimumWidth(i, 1)
        self.tabLayout3.setColumnStretch(i, 1)
    for i in range(0, 40):
        self.tabLayout1.setRowMinimumHeight(i, 1)
        self.tabLayout1.setRowStretch(i, 1)
        self.tabLayout2.setRowMinimumHeight(i, 1)
        self.tabLayout2.setRowStretch(i, 1)
        self.tabLayout3.setRowMinimumHeight(i, 1)
        self.tabLayout3.setRowStretch(i, 1)

    self.btn1 = QPushButton("Select Files")
    self.btn1.clicked.connect(self.selectFiles)
    self.tabLayout1.addWidget(self.btn1, 0, 0, 2, 10)

    self.beginAnalysisButton = QPushButton("Begin Analysis")
    self.beginAnalysisButton.clicked.connect(self.extraction)
    self.tabLayout1.addWidget(self.beginAnalysisButton, 2, 0, 2, 10)
    self.beginAnalysisButton.setDisabled(True)

    tmpobject = QLabel("Number of plots shown during analysis")
    self.tabLayout1.addWidget(tmpobject, 4, 0, 2, 10)
    tmpobject.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    self.plotDivisions = QLineEdit()
    self.tabLayout1.addWidget(self.plotDivisions, 6, 0, 2, 4)
    self.plotDivisions.setText("100")
    self.plotDivisions.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    tmpobject = QLabel("OF")
    self.tabLayout1.addWidget(tmpobject, 6, 4, 2, 2)
    tmpobject.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    self.numObservations = QLineEdit()
    self.tabLayout1.addWidget(self.numObservations, 6, 6, 2, 4)
    self.numObservations.setDisabled(True)
    self.numObservations.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    self.extractData = QCheckBox("Save to CSV")
    self.tabLayout1.addWidget(self.extractData, 8, 0, 2, 10)
    self.extractData.setChecked(False)
    # self.extractData.setEnabled(False)

    self.performFits = QCheckBox("Perform Line Fits")
    self.tabLayout1.addWidget(self.performFits, 10, 0, 2, 10)
    self.performFits.setChecked(True)  # False)

    self.tabLayout1.addWidget(QLabel("Number of Lines"), 12, 0, 3, 6)
    self.numLines = QSpinBox()
    self.tabLayout1.addWidget(self.numLines, 12, 6, 2, 4)
    self.numLines.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.numLines.setValue(2)
    self.numLines.setRange(0, 1000)

    self.tabLayout1.addWidget(QLabel("Background Order"), 14, 0, 2, 6)
    self.backOrder = QSpinBox()
    self.tabLayout1.addWidget(self.backOrder, 14, 6, 2, 4)
    self.backOrder.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.backOrder.setValue(3)

    self.tabLayout1.addWidget(QLabel("Wavelength Order"), 16, 0, 2, 6)
    self.wvlngthOrder = QSpinBox()
    self.tabLayout1.addWidget(self.wvlngthOrder, 16, 6, 2, 4)
    self.wvlngthOrder.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.wvlngthOrder.setValue(1)

    self.plotSignal.connect(self.plotUpdate)
    self.statusSignal.connect(self.statusUpdate)

    # self.tabLayout1.addWidget(QLabel("Isolate Time Range"), 30, 0, 3, 8)
    # self.timeSpanExtract = QCheckBox("Isolate Time Range")#QPushButton("Extract")
    # self.tabLayout1.addWidget(self.timeSpanExtract, 30, 0, 3, 10)
    self.timeSpanExtract = QPushButton(
        "Reload within isolated range"
    )  # QPushButton("Extract")
    self.tabLayout1.addWidget(self.timeSpanExtract, 18, 0, 2, 10)
    # self.timeSpanExtract.clicked.connect(self.saveTimeSpan)
    self.timeSpanExtract.clicked.connect(lambda: self.loadFiles(True))

    self.extractTimes = False

    self.tabLayout1.addWidget(QLabel("Time Format: YYYYMMDD_HHMMSS"), 20, 0, 2, 10)
    self.timeSpanExtract.setChecked(0)

    # Index 1 =

    self.timeNames = []

    self.timeList = [["YYYYMMDD_HHMMSS", "YYYYMMDD_HHMMSS"]]

    self.tabLayout1.addWidget(QLabel("Start Time"), 22, 0, 2, 3)
    self.startTime = QLineEdit()  # "20170720_233600")
    self.tabLayout1.addWidget(self.startTime, 22, 3, 2, 7)

    self.tabLayout1.addWidget(QLabel("End Time"), 24, 0, 2, 3)
    self.endTime = QLineEdit()  # "20170720_234100")
    self.tabLayout1.addWidget(self.endTime, 24, 3, 2, 7)

    self.reloadOriginalData = QPushButton("Reload full file")
    self.tabLayout1.addWidget(self.reloadOriginalData, 26, 0, 2, 10)
    self.reloadOriginalData.clicked.connect(lambda: self.loadFiles(False))

    # self.loadNCButton = QPushButton("Load NetCDF")
    self.loadNCButton = QPushButton("Process CWC")
    self.tabLayout1.addWidget(self.loadNCButton, 28, 0, 2, 10)
    self.loadNCButton.clicked.connect(self.loadNC)

    self.timeMenu = QComboBox()
    self.tabLayout1.addWidget(self.timeMenu, 36, 0, 3, 10)
    self.timeMenu.setStyleSheet("QComboBox { combobox-popup: 0; }")
    self.timeMenu.addItems(self.timeNames)
    self.timeMenu.setMaxVisibleItems(15)
    self.timeMenu.currentIndexChanged.connect(self.updateInterval)
    self.timeMenu.setVisible(False)

    self.figure = plt.figure()
    self.canvas = FigureCanvas(self.figure)
    self.toolbar = NavigationToolbar(self.canvas, self)

    self.tabLayout1.addWidget(self.toolbar, 0, 15, 2, 85)
    self.tabLayout1.addWidget(self.canvas, 2, 15, 28, 85)

    self.figMenu = QComboBox()
    self.tabLayout1.addWidget(self.figMenu, 30, 15, 3, 80)
    self.figMenu.setStyleSheet("QComboBox { combobox-popup: 0; }")
    self.figMenu.addItems(self.timeNames)
    self.figMenu.setMaxVisibleItems(15)
    self.figMenu.setVisible(False)
    self.figMenu.addItems(
        [
            "VMR Observations",
            "Cell Temps",
            "Pressure",
            "Mass Flow",
            "Laser and Detector Temps",
            "Sample Scan",
        ]
    )
    self.figMenu.currentIndexChanged.connect(
        lambda: self.plotResults(
            self.HK, self.SC, self.ints, "", self.figMenu.currentIndex()
        )
    )

    self.progress = QProgressBar()
    self.tabLayout1.addWidget(self.progress, 33, 15, 3, 85)

    ######################################################################################
    ########################### TAB 3 HITRAN MODELING ####################################
    ######################################################################################

    self.loadHitranButton = QPushButton("Select Files")
    self.loadHitranButton.clicked.connect(lambda: self.loadHitran(True))
    self.tabLayout3.addWidget(self.loadHitranButton, 0, 0, 2, 10)

    self.loadHitran(False)

    self.hitranFile = None

    self.loadHitranButton = QPushButton("Process Spectra")
    self.loadHitranButton.clicked.connect(self.processHitran)
    self.tabLayout3.addWidget(self.loadHitranButton, 2, 0, 2, 10)

    self.hitranDomainLabel = QLabel("Wavelength Domain (nm)")
    self.tabLayout3.addWidget(self.hitranDomainLabel, 4, 0, 2, 10)
    self.hitranDomainLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    self.hitranMinLabel = QLabel("Minimum (nm)")
    self.tabLayout3.addWidget(self.hitranMinLabel, 6, 0, 2, 5)
    self.hitranMin = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranMin, 6, 5, 2, 5)
    self.hitranMin.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranMin.setRange(0.00, 1000000.00)
    self.hitranMin.setDecimals(5)
    # self.hitranMin.setValue(1372.4)#1371.835)
    self.hitranMin.setValue(1368.5)  # 1371.835)

    self.hitranMaxLabel = QLabel("Maximum (nm)")
    self.tabLayout3.addWidget(self.hitranMaxLabel, 8, 0, 2, 5)
    self.hitranMax = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranMax, 8, 5, 2, 5)
    self.hitranMax.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranMax.setRange(0.00, 1000000.00)
    self.hitranMax.setDecimals(5)
    # self.hitranMax.setValue(1372.6)#1373.165)
    self.hitranMax.setValue(1368.7)

    self.maxHitranDiv = 10000000

    self.hitranResLabel = QLabel("Resolution (nm)")
    self.tabLayout3.addWidget(self.hitranResLabel, 10, 0, 2, 5)
    self.hitranRes = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranRes, 10, 5, 2, 5)
    self.hitranRes.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranRes.setRange(0.00, 1000000.00)
    self.hitranRes.setDecimals(8)
    self.hitranRes.setValue(
        np.abs(self.hitranMax.value() - self.hitranMin.value()) / self.maxHitranDiv
    )
    self.hitranRes.setValue(0.000002)

    self.hitranCushLabel = QLabel("Window Xcess (nm)")
    self.tabLayout3.addWidget(self.hitranCushLabel, 12, 0, 2, 5)
    self.hitranCush = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranCush, 12, 5, 2, 5)
    self.hitranCush.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranCush.setRange(0.00, 1000000.00)
    self.hitranCush.setDecimals(5)
    self.hitranCush.setValue(0.0)  # 1.0)

    self.tabLayout3.addWidget(QLabel("Wavelength"), 14, 0, 2, 5)
    self.tabLayout3.addWidget(QLabel("Wavenumber"), 16, 0, 2, 5)

    self.wavelengthOption = QRadioButton()
    self.tabLayout3.addWidget(self.wavelengthOption, 14, 7, 2, 2)
    self.wavenumberOption = QRadioButton()
    self.tabLayout3.addWidget(self.wavenumberOption, 16, 7, 2, 2)
    self.wavelengthOption.setChecked(True)
    self.wavelengthOption.setDisabled(True)

    self.wavelengthOption.clicked.connect(lambda: self.hitranDomainSwap(1))
    self.wavenumberOption.clicked.connect(lambda: self.hitranDomainSwap(2))

    self.tabLayout3.addWidget(QLabel("Molecule"), 18, 0, 2, 5)
    self.molMenu = QComboBox()
    self.tabLayout3.addWidget(self.molMenu, 18, 5, 2, 5)
    # self.molMenu.setStyleSheet("QComboBox { combobox-popup: 0; }");
    self.molMenu.addItems(self.timeNames)
    self.molMenu.setMaxVisibleItems(15)
    # self.molMenu.setVisible(False)
    # self.molMenu.addItems(['Undefined'])#'VMR Observations','Cell Temps', 'Pressure', 'Mass Flow', 'Laser and Detector Temps', 'Sample Scan'])

    self.tabLayout3.addWidget(QLabel("Isotopologue"), 20, 0, 2, 5)
    self.isoMenu = QComboBox()
    self.tabLayout3.addWidget(self.isoMenu, 20, 5, 2, 5)
    # self.isoMenu.setStyleSheet("QComboBox { combobox-popup: 0; }");
    self.isoMenu.addItems(self.timeNames)
    self.isoMenu.setMaxVisibleItems(15)
    # self.molMenu.setVisible(False)
    # self.isoMenu.addItems(['Undefined'])#'VMR Observations','Cell Temps', 'Pressure', 'Mass Flow', 'Laser and Detector Temps', 'Sample Scan'])

    self.molMenu.currentIndexChanged.connect(
        lambda: self.hitranIDChange(False)
    )  # (self.HK,self.SC,self.ints,'',self.figMenu.currentIndex()))
    self.isoMenu.currentIndexChanged.connect(
        lambda: self.hitranIDChange(False)
    )  # (self.HK,self.SC,self.ints,'',self.figMenu.currentIndex()))

    self.tabLayout3.addWidget(QLabel("VMR (ppmv)"), 22, 0, 2, 5)
    self.hitranVMR = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranVMR, 22, 5, 2, 5)
    self.hitranVMR.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranVMR.setRange(0.00, 1000000.00)
    self.hitranVMR.setDecimals(2)
    self.hitranVMR.setValue(10000.00)
    self.hitranVMR.setDisabled(True)

    self.tabLayout3.addWidget(QLabel("Fractionation (permil)"), 24, 0, 2, 5)
    self.hitranFrac = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranFrac, 24, 5, 2, 5)
    self.hitranFrac.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranFrac.setRange(-1000.00, 1000000.00)
    self.hitranFrac.setDecimals(4)
    self.hitranFrac.setValue(0.00)
    self.hitranFrac.setDisabled(True)

    self.hitranVMR.valueChanged.connect(lambda: self.hitranIDChange(True))
    self.hitranFrac.valueChanged.connect(lambda: self.hitranIDChange(True))
    # self.hitranVMR.editingFinished.connect(lambda: self.hitranIDChange(True))
    # self.hitranFrac.editingFinished.connect(lambda: self.hitranIDChange(True))

    self.resetHitranAbundancesButton = QPushButton("Reset Isotope Abundances")
    self.resetHitranAbundancesButton.clicked.connect(self.resetHitranAbundances)
    self.tabLayout3.addWidget(self.resetHitranAbundancesButton, 24, 0, 2, 10)
    self.resetHitranAbundancesButton.setVisible(False)

    self.tabLayout3.addWidget(QLabel("Pressure (hPa)"), 26, 0, 2, 5)
    self.hitranPress = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranPress, 26, 5, 2, 5)
    self.hitranPress.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranPress.setRange(0.00, 2000.00)
    self.hitranPress.setDecimals(2)
    self.hitranPress.setValue(400.00)

    self.tabLayout3.addWidget(QLabel("Temperature (C)"), 28, 0, 2, 5)
    self.hitranTemp = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranTemp, 28, 5, 2, 5)
    self.hitranTemp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranTemp.setRange(-100.00, 200.00)
    self.hitranTemp.setDecimals(2)
    self.hitranTemp.setValue(25.00)

    self.tabLayout3.addWidget(QLabel("Path Length (cm)"), 30, 0, 2, 5)
    self.hitranPath = QDoubleSpinBox()
    self.tabLayout3.addWidget(self.hitranPath, 30, 5, 2, 5)
    self.hitranPath.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    self.hitranPath.setRange(0, 1000000.00)
    self.hitranPath.setDecimals(2)
    # self.hitranPath.setValue(7200.00)#60.00)
    self.hitranPath.setValue(60.00)

    self.progress = QProgressBar()
    self.tabLayout1.addWidget(self.progress, 33, 15, 3, 85)

    self.plotHitranButton = QPushButton("Plot Spectra Within Specified Parameters")
    self.plotHitranButton.clicked.connect(self.plotHitran)
    self.tabLayout3.addWidget(self.plotHitranButton, 0, 10, 2, 90)
    self.plotHitranButton.setDisabled(True)

    self.hitranFigure = plt.figure()
    self.hitranCanvas = FigureCanvas(self.hitranFigure)
    self.hitranToolbar = NavigationToolbar(self.hitranCanvas, self)

    self.tabLayout3.addWidget(self.hitranToolbar, 2, 15, 2, 85)
    self.tabLayout3.addWidget(self.hitranCanvas, 4, 15, 26, 85)

    self.hitranProgress = QProgressBar()
    self.tabLayout3.addWidget(self.hitranProgress, 34, 0, 3, 100)

    ######################################################################################
    ######################################################################################
    ######################################################################################
    ######################################################################################
    ######################################################################################
    ######################################################################################

    self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)
    self.setLayout(self.gridLayout)
    # MainWindow.setCentralWidget(self.centralWidget)

    self.statusBar = QLineEdit()
    self.tabLayout1.addWidget(self.statusBar, 36, 0, 5, 100)
    self.statusBar.setText("Press the select files to begin")

    self.closeTrigger = False
