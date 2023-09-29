from common.libraryImports import *


def initUI(self):

    try:
        if sys.argv[1] == "batch":
            batchArg = True
            basePath = "./"
            fileList = os.listdir(basePath)
            fileList = [basePath + str(x) for x in fileList]
            fileList = list(filter(lambda x: ".nc" in x, fileList))
            batchOrder = -1
    except:
        batchArg = False
        fileList = []
        batchOrder = -1
        # except: pass

    self.setWindowTitle(self.title)
    # self.setGeometry(self.left, self.top, self.width, self.height)

    self.fileList = fileList
    self.batchOrder = batchOrder
    self.batchArg = batchArg

    # self.centralWidget = QtWidgets.QWidget()
    # self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)

    # self.layout = QtWidgets.QGridLayout(self.centralWidget)
    # self.layout.setContentsMargins(5, 5, 5, 5)
    # self.layout.setSpacing(5)

    # for i in range(0, 100):
    # 	self.layout.setColumnMinimumWidth(i,1)
    # 	self.layout.setColumnStretch(i,1)
    # for i in range(0, 40):
    # 	self.layout.setRowMinimumHeight(i,1)
    # 	self.layout.setRowStretch(i,1)

    self.layout = QtWidgets.QGridLayout()  # QVBoxLayout()         # Set box for plotting
    # self.vbl.addWidget(self.canvas)

    self.loadBtn = QPushButton("Select UHSAS File")
    self.loadBtn.clicked.connect(self.loadData)  # lambda: self.loadHitran(True))
    # self.btn1.clicked.connect(self.selectFiles)
    self.layout.addWidget(self.loadBtn, 0, 0, 1, 4)  # , 5, 5, 10, 10)

    self.saveBtn = QPushButton("Save Reduced Data")
    # self.saveBtn.clicked.connect(self.saveData)
    self.layout.addWidget(self.saveBtn, 0, 4, 1, 2)
    self.saveBtn.setDisabled(True)
    self.saveBtn.clicked.connect(self.saveData)

    self.saveReanalysis = QPushButton("Save Reanalysis")
    # self.plotBtn.clicked.connect(self.plotBtn)
    self.layout.addWidget(self.saveReanalysis, 0, 6, 1, 2)
    self.saveReanalysis.setDisabled(True)
    self.saveReanalysis.clicked.connect(self.saveData)

    self.canvas = MatplotlibWidget()
    # self.canvas.setStyleSheet("background-color:transparent;")
    self.figure = self.canvas.getFigure()  # .add_subplot(111)

    # self.toolbar = self.canvas.toolbar
    # self.toolbar.c

    # Load toolbar information
    # self.toolbar = NavigationToolbar(self.canvas, self)

    # self.figure.add_subplot(111)
    self.figure.patch.set_facecolor("None")
    # self.figure.tight_layout()

    self.figure.canvas.mpl_connect("button_press_event", self.plotClick)
    self.figure.canvas.mpl_connect("scroll_event", self.zoomFunction)
    self.layout.addWidget(self.canvas, 1, 0, 16, 4)

    self.figure.clear()
    # ax = self.figure.add_subplot(111)
    self.ax = self.figure.subplots()
    # self.ax = self.figure.gca()
    self.ax.callbacks.connect("xlim_changed", self.zoomFunction)  # self.plotClick)
    # lambda x=True: self.plotClick(x)

    # def on_xlim_change(*args):
    #    print "do your pushing and popping here..."
    # ax = gca()
    # ax.callbacks.connect('xlim_changed',on_xlim_change)

    # self.canvas.setObjectName(_fromUtf8("journalEntry"))

    # self.figure = plt.figure(tight_layout=True)
    # self.fig = Figure(tight_layout=True)

    # self.canvas = FigureCanvas(self.figure)
    # self.canvas.mpl_connect("button_press_event", self.plotClick)

    # self.toolbar = NavigationToolbar(self.canvas, self)

    # self.layout.addWidget(self.toolbar, 1, 0, 1, 1)  # , 0, 15, 2, 85)
    # self.layout.addWidget(self.canvas, 2, 0, 1, 1)  # , 2, 15, 28, 85)

    self.histCanvas = MatplotlibWidget()
    self.histFigure = self.histCanvas.getFigure()  # .add_subplot(111)

    self.histFigure.clear()
    self.histax = self.histFigure.subplots()
    # self.histFigure.tight_layout()
    self.histFigure.patch.set_facecolor("None")
    # self.histFigure.add_subplot(111)
    # self.histFigure.tight_layout()
    # self.histFigure.canvas.mpl_connect("button_press_event", self.plotClick)
    self.layout.addWidget(self.histCanvas, 1, 4, 16, 2)

    sizePolicy = QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
    )
    sizePolicy.setHorizontalStretch(2)
    sizePolicy.setVerticalStretch(0)

    sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
    self.canvas.setSizePolicy(sizePolicy)
    # self.canvas.setMinimumSize(QtCore.QSize(400, 200))

    sizePolicy.setHorizontalStretch(2)
    sizePolicy.setVerticalStretch(0)

    sizePolicy.setHeightForWidth(self.histCanvas.sizePolicy().hasHeightForWidth())
    self.histCanvas.setSizePolicy(sizePolicy)
    # self.histCanvas.setMinimumSize(QtCore.QSize(300, 200))

    # Global plotting options
    plt.rcParams.update({"font.size": 7, "font.weight": "bold"})

    # self.histFigure = plt.figure(tight_layout=True)
    # plt.style.use('dark_background')
    # self.histCanvas = FigureCanvas(self.histFigure)
    # self.histToolbar = NavigationToolbar(self.histCanvas, self)
    # self.layout.addWidget(self.histToolbar, 1, 1, 1, 2)
    # self.layout.addWidget(self.histCanvas, 2, 1, 1, 2)
    # self.histCanvas.setDisabled(True)

    self.label = QLabel(
        "Click anywhere on time histogram to plot histogram at selected time"
    )
    # self.layout.addWidget(self.label,3,0,1,1)
    # self.label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)

    self.figMenu = QComboBox()
    self.layout.addWidget(self.figMenu, 17, 0, 1, 4)  # , 30, 15, 3, 80)
    self.figMenu.setStyleSheet("QComboBox { combobox-popup: 0; }")

    self.dataNames = ["dN/dlogD by Time", "dM/dlogD by Time"]  #
    # extraNames = ['Accum (s)','Scatter (V)', 'Current (V)', 'Sample (V)', 'Ref. (V)', 'Temp (V)',\
    # 	'Sheath (sccm)','Diff. (V)', 'Box (K)', 'Purge (sccm)', 'Pres. (kPa)', 'Aux. (V)', 'Flow (sccm)']
    self.figMenu.addItems(self.dataNames)

    # 		self.figMenu.setDisabled(False)
    # self.figMenu.addItems(self.timeNames)
    self.figMenu.setMaxVisibleItems(15)
    self.figMenu.setVisible(True)
    self.figMenu.setDisabled(True)
    self.figMenu.setCurrentIndex(0)
    self.figMenu.currentIndexChanged.connect(lambda x=False: self.primaryPlotting(x))
    # self.figMenu.currentIndexChanged.connect(lambda: self.plotResults(self.HK,self.SC,self.ints,'',self.figMenu.currentIndex()))

    self.histFigMenu = QComboBox()
    self.layout.addWidget(self.histFigMenu, 17, 4, 1, 2)
    self.histFigMenu.setStyleSheet("QComboBox { combobox-popup: 0; }")
    self.histFigMenu.setMaxVisibleItems(15)
    self.histFigMenu.setVisible(True)
    self.histFigMenu.setDisabled(True)

    self.histFigKeys = [
        "dN/dlogD Histogram",
        "dM/dlogD Histogram",
        "Windowed Histogram dN/dLogD Overlays",
        "Windowed Averaged dN/dLogD Histogram",
        "Concentration at selected Size",
        "Mass at selected size",
        "Average Concentration vs Time",
        "Average Mass vs Time",
        "Peak Size",
        "Peak Value",
        "N (total)",
        "n(1 - 33)",
        "n(34 - 66)",
        "n(67 - 99)",
        "n (total # density)",
        "v (volume density)",
    ]

    # Append fit parameters once they have been completed.

    # The variables that are worth having in a "reduced data" file are:
    # Date, Time, Mode, Sample flow, Temp, Pres, N(tot), n(1-33), n(34-66), n(67-99), n, v, useful fit parameters...
    # Mode = inlet (CVI, Total, SDI)
    # N(tot) is particle counts summed over 99 bins
    # n(1-33) is number density (i.e., number of particles divided by the flow rate) in first 33 bins
    # n(34-66) is number density in second 33 bins
    # n(67-99) is number density in third 33 bins
    # n is total number density, and is probably the same value as CVIU, or whatever is currently in the exchange files for the CVI.
    # v is volume density (in microns^3 per cm^3) for full 99 bins
    # we can iterate 'useful fit parameters' based on a looking at a few flights, but I'm guessing:
    # D1(max) is diameter at maximum number in the first gaussian mode based on fits
    # D2(max) is the diameter at maximum number in the second gaussian mode based on fits
    # D3 (if there is a third mode - strike if not)

    self.histFigMenu.addItems(self.histFigKeys)

    # Create reanalysis dictionary based on items in histFigMenu
    self.reanalysisDict = {}
    self.reanalysisDict.fromkeys(self.histFigKeys)

    for key in self.histFigKeys:
        self.reanalysisDict[key] = {}
        self.reanalysisDict[key]["title"] = ""
        self.reanalysisDict[key]["xlabel"] = ""
        self.reanalysisDict[key]["ylabel"] = ""
        self.reanalysisDict[key]["domain"] = []
        self.reanalysisDict[key]["range"] = []
        if "ist" in key:
            self.reanalysisDict[key]["fit"] = {}
            self.reanalysisDict[key]["fit_label"] = ""

    # self.histFigMenu.addItems([])
    self.histFigMenu.currentIndexChanged.connect(self.plotClick)

    tmp = QLabel("Fit Options")
    tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(tmp, 1, 6, 1, 2)

    tmp = QLabel("Number of Modes")
    tmp.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
    self.layout.addWidget(tmp, 2, 6, 1, 1)

    self.numModes = QSpinBox()
    self.numModes.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(self.numModes, 2, 7, 1, 1)
    self.numModes.setValue(1)

    tmp = QLabel("Allow Offset?")
    tmp.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)
    self.layout.addWidget(tmp, 3, 6, 1, 1)

    self.varyOffset = QCheckBox()
    # self.varyOffset.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(self.varyOffset, 3, 7, 1, 1)

    tmp = QLabel("Fit Minimum (nm)")
    tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(tmp, 4, 6, 1, 1)

    self.fitMin = QSpinBox()
    self.fitMin.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(self.fitMin, 4, 7, 1, 1)
    self.fitMin.setMinimum(0)
    self.fitMin.setMaximum(10000)
    self.fitMin.setValue(0)

    tmp = QLabel("Fit Maximum (nm)")
    tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(tmp, 5, 6, 1, 1)

    self.fitMax = QSpinBox()
    self.fitMax.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
    self.layout.addWidget(self.fitMax, 5, 7, 1, 1)
    self.fitMax.setMinimum(0)
    self.fitMax.setMaximum(10000)
    self.fitMax.setValue(1000)

    self.fitOutput = QPlainTextEdit()
    self.layout.addWidget(self.fitOutput, 6, 6, 12, 2)
    self.fitOutput.setWordWrapMode(QTextOption.NoWrap)
    self.fitOutput.setSizePolicy(sizePolicy)

    self.fitOutput.setFocus()

    self.numModes.editingFinished.connect(lambda x=False: self.plotClick(x))
    self.varyOffset.stateChanged.connect(lambda x=False: self.plotClick(x))
    self.fitMin.editingFinished.connect(lambda x=False: self.plotClick(x))
    self.fitMax.editingFinished.connect(lambda x=False: self.plotClick(x))

    self.progress = QProgressBar()
    self.progress.setMinimum(0)
    self.progress.setMaximum(100)
    self.progress.setValue(0)
    self.layout.addWidget(self.progress, 18, 0, 1, 8)  # , 33, 15, 3, 85)

    # self.gridLayout.addWidget(self.centralWidget, 0, 0, 50, 50)
    # self.setLayout(self.gridLayout)
    # MainWindow.setCentralWidget(self.centralWidget)

    self.setLayout(self.layout)
    # self.statusBar = QLineEdit()
    # self.layout.addWidget(self.statusBar, 36, 0, 5, 100)
    # self.statusBar.setText("Press the select files to begin")

    self.threadpool = QThreadPool()
    # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    self.freq = 1000
    self.dur = 10000

    # print(batchArg)
    if self.batchArg:  # == 'batch':
        self.loadBtn.click()


# 	def mousePressEvent(self, QMouseEvent):
# 		cursor = QtGui.QCursor()
# 		print(cursor.pos())#QMouseEvent.pos()

# 	def mouseReleaseEvent(self, QMouseEvent):
# 		cursor = QtGui.QCursor()
# 		print(cursor.pos())
