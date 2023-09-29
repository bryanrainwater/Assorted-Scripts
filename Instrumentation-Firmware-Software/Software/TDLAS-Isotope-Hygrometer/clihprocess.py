import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#from PyQt5.QtGui import *

import numpy as np
import math
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from matplotlib import animation


#import scipy
from scipy import *
#from scipy.optimize import leastsq

from numpy import exp, pi, sqrt
from scipy.special import erf, erfc, wofz
import scipy.integrate as integrate

#from scipy.signal import savgol_filter

from scipy.signal import butter, filtfilt

#import scipy.io.array_import

#For minimize function
from lmfit import fit_report, Parameters, minimize
from time import time

from lmfit import Model, CompositeModel
from lmfit.models import ConstantModel, ExpressionModel, LinearModel, VoigtModel, PolynomialModel, QuadraticModel, ExponentialModel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from jdcal import *
import time

import csv

#NOTES

# Appears to be an issue when creating large merge files and then trying to
#	average them (causes segmentation fault)

# There appears to be a single point offset in time between older voigt processing
#	and this new python code. (i.e. old codes time 6 equal to new codes time 5)

# Need to implement refined guessing routine such that it always uses the previous
#	successful fits for next guess UNLESS there is chunk of time missing
#	OR there appears to be some sort of divergent fit

# Need to implement some sort of narrowing function for allowing higher precision
#	fits of the smaller absorption features (set mins and maxes as well)

# Implement better initial guessing routine (i.e. average all scans OR
#	find well behaved signal to fit to prevent error prone initialization


class Ui_MainWindow(QWidget):

	def __init__(self, parent=None):
		super(Ui_MainWindow, self).__init__(parent)
		self.title = 'PyQt5 file dialogs'
		self.left = 10
		self.top = 10
		self.width = 960 
		self.height = 540
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)


		self.centralWidget = QtWidgets.QWidget()
		self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
		
		self.tabWidget = QtWidgets.QTabWidget(self.centralWidget)
		self.tabWidget.setStyleSheet("""QTabWidget{background-color: rgb(220,220,255);}""")

		self.tab1 = QtWidgets.QWidget()
		self.tabWidget.addTab(self.tab1, "Tab1")
		
		self.tabLayout1 = QtWidgets.QGridLayout(self.tab1)
		self.tabLayout1.setContentsMargins(10, 10, 10, 10)
		self.tabLayout1.setSpacing(5)

		for i in range(0, 100):
			self.tabLayout1.setColumnMinimumWidth(i,1)
			self.tabLayout1.setColumnStretch(i,1)
		for i in range(0, 50):
			self.tabLayout1.setRowMinimumHeight(i,1)
			self.tabLayout1.setRowStretch(i,1)


		self.btn1 = QPushButton("Select Files")
		self.btn1.clicked.connect(self.extraction)
		self.tabLayout1.addWidget(self.btn1, 0, 0, 3, 10)

		self.extractData = QCheckBox("Save to CSV")
		self.tabLayout1.addWidget(self.extractData, 3, 0, 3, 10)
		self.extractData.setChecked(False)
		#self.extractData.setEnabled(False)

		self.performFits = QCheckBox("Perform Line Fits")
		self.tabLayout1.addWidget(self.performFits, 6, 0, 3, 10)
		self.performFits.setChecked(True)


		self.tabLayout1.addWidget(QLabel("Number of Lines"), 9,0,3,10)
		self.numLines = QSpinBox()
		self.tabLayout1.addWidget(self.numLines, 12, 0, 3, 10)
		self.numLines.setValue(4)

		self.tabLayout1.addWidget(QLabel("Background Order"), 15, 0, 3, 10)
		self.backOrder = QSpinBox()
		self.tabLayout1.addWidget(self.backOrder, 18, 0, 3, 10)
		self.backOrder.setValue(2)

		self.tabLayout1.addWidget(QLabel("Wavelength Order"), 21, 0, 3, 10)
		self.wvlngthOrder = QSpinBox()
		self.tabLayout1.addWidget(self.wvlngthOrder, 24, 0, 3, 10)
		self.wvlngthOrder.setValue(2)

		#self.tabLayout1.addWidget(QLabel("Isolate Time Range"), 30, 0, 3, 8)
		self.timeSpanExtract = QCheckBox("Isolate Time Range")#QPushButton("Extract")
		self.tabLayout1.addWidget(self.timeSpanExtract, 30, 0, 3, 10)
		#self.timeSpanExtract.clicked.connect(self.saveTimeSpan)

		self.tabLayout1.addWidget(QLabel("Time Format: YYYYMMDD_HHMMSS"), 33, 0, 3, 10)
		self.timeSpanExtract.setChecked(1)	

		#Index 1 =

		self.timeNames = [
		'2.6um, P = 202, PPMv = 128',
		'2.6um, P = 198, PPMv = 950',
		'2.6um, P = 193, PPMv = 3325',
		'2.6um, P = 190, PPMv = 5000',
		'2.6um, P = 187, PPMv = 8710',
		'2.6um, P = 408, PPMv = 70',
		'2.6um, P = 399, PPMv = 825',
		'2.6um, P = 390, PPMv = 3130',
		'2.6um, P = 374, PPMv = 4675',
		'2.6um, P = 410, PPMv = 8718',
		'2.6um, P = 575, PPMv = 820',
		'2.6um, P = 594, PPMv = 2650',
		'2.6um, P = 595, PPMv = 4800',
		'2.6um, P = 576, PPMv = 8700',
		'1.37um-r, 2.682v, P = 203.5, PPMv = 50',
		'1.37um-p, 2.592v, P = 203.5, PPMv = 45',
		'1.37um-p, 2.592v, P = 198, PPMv = 750',
		'1.37um-r, 2.691v, P = 198, PPMv = 750',
		'1.37um-r, 2.690v, P = 194, PPMv = 2410',
		'1.37um-p, 2.591v, P = 194, PPMv = 2410',
		'1.37um-p, 2.590v, P = 188, PPMv = 5260',
		'1.37um-r, 2.690v, P = 188, PPMv = 5260',
		'1.37um-r, 2.691v, P = 188, PPMv = 8640',
		'1.37um-p, 2.590v, P = 188, PPMv = 8640',
		'1.37um-p, 2.590v, P = 412, PPMv = 110',
		'1.37um-r, 2.690v, P = 412, PPMv = 110',
		'1.37um-r, 2.691v, P = 402, PPMv = 680',
		'1.37um-p, 2.591v, P = 402, PPMv = 680',
		'1.37um-p, 2.592v, P = 402, PPMv = 2220',
		'1.37um-r, 2.691v, P = 402, PPMv = 2220',
		'1.37um-r, 2.691v, P = 386, PPMv = 4550',
		'1.37um-p, 2.592v, P = 386, PPMv = 4550',
		'1.37um-p, 2.592v, P = 400, PPMv = 8695',
		'1.37um-r, 2.694v, P = 400, PPMv = 8695',
		'1.37um-r, 2.694v, P = 600, PPMv = 580',
		'1.37um-p, 2.590v, P = 600, PPMv = 580',
		'1.37um-p, 2.590v, P = 604, PPMv = 3990',
		'1.37um-r, 2.690v, P = 604, PPMv = 3900',
		'1.37um-r, 2.689v, P = 599, PPMv = 8690',
		'1.37um-p, unknwn, P = 599, PPMv = 8690',
		'PP2F 2.6um, P = 60, PPMv = 204']
		

		self.timeList = [
		["20170720_233600","20170720_234100"],
		["20170720_234700","20170720_235200"],
		["20170720_235800","20170721_000300"],
		["20170721_000800","20170721_001300"],
		["20170721_001700","20170721_002000"],
		["20170721_003000","20170721_003500"],
		["20170721_004000","20170721_004500"],
		["20170721_005000","20170721_005500"],
		["20170721_005900","20170721_010400"],
		["20170721_011200","20170721_011700"],
		["20170721_012400","20170721_012900"],
		["20170721_014100","20170721_014600"],
		["20170721_014800","20170721_015300"],
		["20170721_015400","20170721_015900"],
		["20170721_164800","20170721_165200"],
		["20170721_165300","20170721_165800"],
		["20170721_170300","20170721_170800"],
		["20170721_170900","20170721_171400"],
		["20170721_171900","20170721_172400"],
		["20170721_172600","20170721_173100"],
		["20170721_173400","20170721_173900"],
		["20170721_174100","20170721_174600"],
		["20170721_175000","20170721_175500"],
		["20170721_175700","20170721_180200"],
		["20170721_182000","20170721_182500"],
		["20170721_182600","20170721_183100"],
		["20170721_183500","20170721_184000"],
		["20170721_184100","20170721_184600"],
		["20170721_185500","20170721_190000"],
		["20170721_190100","20170721_190600"],
		["20170721_190900","20170721_191400"],
		["20170721_191500","20170721_192000"],
		["20170721_192600","20170721_193100"],
		["20170721_193200","20170721_193700"],
		["20170721_194600","20170721_201600"],
		["20170721_201700","20170721_202200"],
		["20170721_202700","20170721_203200"],
		["20170721_203300","20170721_203800"],
		["20170721_204100","20170721_204600"],
		["20170721_204700","20170721_205200"],
		["20170721_155000","20170721_160000"]]


	
		self.tabLayout1.addWidget(QLabel("Start Time"), 36, 0, 3, 3)
		self.startTime = QLineEdit("20170720_233600")
		self.tabLayout1.addWidget(self.startTime, 36, 3, 3, 7)

		self.tabLayout1.addWidget(QLabel("End Time"), 39, 0, 3, 3)
		self.endTime = QLineEdit("20170720_234100")
		self.tabLayout1.addWidget(self.endTime, 39, 3, 3, 7)


		self.timeMenu = QComboBox()
		self.tabLayout1.addWidget(self.timeMenu, 42, 0, 3, 10) 
		self.timeMenu.setStyleSheet("QComboBox { combobox-popup: 0; }");
		self.timeMenu.addItems(self.timeNames)
		self.timeMenu.setMaxVisibleItems(15)
		self.timeMenu.currentIndexChanged.connect(self.updateInterval)


		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)

		self.tabLayout1.addWidget(self.toolbar, 0, 15, 2, 80)
		self.tabLayout1.addWidget(self.canvas, 2, 15, 40, 80)

		self.progress = QProgressBar()
		self.tabLayout1.addWidget(self.progress, 42, 15, 8, 80)


		self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)
		self.setLayout(self.gridLayout)
		#MainWindow.setCentralWidget(self.centralWidget)
		
		#QtCore.QMetaObject.connectSlotsByName(MainWindow)

		#self.btn1.click()


		#self.extraction()

		#self.show()


	def updateInterval(self):
		self.startTime.setText(self.timeList[self.timeMenu.currentIndex()][0])
		self.endTime.setText(self.timeList[self.timeMenu.currentIndex()][1])

	def extraction(self):
		#files = self.openFileNamesDialog()

		files = ['/mnt/c/Users/rainw/Desktop/JPL_July_Visit/JPL_CLiH_Data_Purge_7-21-17/CLH2-20170720_1648_HK_merged','/mnt/c/Users/rainw/Desktop/JPL_July_Visit/JPL_CLiH_Data_Purge_7-21-17/CLH2-20170720_1648_SC_merged']

		self.basepath = files[0]
		self.basepath = '/'.join(self.basepath.split('/')[:-1]) + '/' + self.timeMenu.currentText().replace(",","_").replace(" ","") + '.dat'
		print(self.basepath)
		#print(files)

		app.processEvents()

		if files: 
			if len(files)>=2:
				files = self.mergefiles(files)
			elif len(files) < 2:
				return

			self.canvas.draw()

			saveCSV = self.extractData.isChecked()

			HK = self.readHK(files[0], saveCSV)
			print('loaded HK')
			SC = self.readSC(files[1], saveCSV)
			print('loaded SC')		

			HK['juldate'] = self.fixjuldate(HK['juldate'])
			SC['juldate'] = self.fixjuldate(SC['juldate'])

			#x = np.arange(len(SC['scans'][0,:]))
			#plt.plot(x,(np.gradient(SC['scans'][0,:])))
			#plt.plot(x,SC['scans'][100,:])
			#plt.show()
			#input('hello')

			#runlen = 100
			#tmpscan = np.zeros(len(SC['scans'][0,:]))
			for i in range(SC['scans'].shape[0]):
				#for j in range(len(SC['scans'][i,:])):
				#	tmpscan[j] = np.mean(SC['scans'][i,-runlen+j:runlen+j])
				
				#plt.plot(x,np.gradient(tmpscan))
				#plt.plot(x,np.gradient(SC['scans'][i,:])
				#plt.show()
				#input("wait")

				tmpmax = np.argmax(np.abs(SC['scans'][i,:]));
				#print(tmpmax);
				SC['scans'][i,:] = np.r_[SC['scans'][i,tmpmax:],SC['scans'][i,:tmpmax]];			
			#plt.plot(SC['scans'][0,:])
			#plt.show()			

			#np.save('/mnt/c/Users/rainw/Desktop/github/CLH2/python/sampleSpectra',SC['scans'][0,:])

			[HK,SC] = self.averageonehz(HK,SC)

			#20 for upscale worked for proxy lines, 10 worked for real
			
			#self.upscale = 10
			#For normalizing the spectra to account for various coadds
			#dims = SC['scans'].shape
			#for i in range(dims[0]):
			#	SC['scans'][i,:] = SC['scans'][i,:]/np.linalg.norm(SC['scans'][i,:])

			numDark = 128#150#45
			fitlen = 100
			celltemp = np.mean(np.c_[HK['temp1'],HK['temp2']],1)

			plotscans = 1
			figdir = 1
			ints = self.lineint(SC['scans'], numDark, plotscans, fitlen, HK['press'],celltemp,figdir)

			#for key, value in ints.items():
			#	print(key)

			fitparams = -9999


			datestring = ''.join(''.join(''.join(str(files[0]).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
			outName = '/'.join(files[0].split('/')[:-1])+'/'+'CLH2-'+datestring+'_packaged_.txt'
			datestring = ''.join(datestring.split('_')[0])

			seconds = np.round((HK['juldate'] - 
				gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[0]-
				gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[1])*86400)
			
			self.seconds = seconds

			if self.performFits.isChecked():
				fitparams = self.linefits(ints,HK, SC['scans'], numDark, self.backOrder.value(), self.numLines.value(), self.wvlngthOrder.value())

			CLHtime = self.saveText(HK,ints,fitparams,outName)
			#self.plotResults(CLHtime,HK,SC,ints)	

	def mergefiles(self,files):
		filestomerge = []
		for file in files:
			if '_HK' in file[-3:]:
				tmpstring = [s for s in files if file[:-3]+'_SC'==s]
				if len(tmpstring) == 1:
					filestomerge.append(file)
					filestomerge.append(tmpstring[0])
	
		mergedfiles = []
		if len(filestomerge)>2:
			mergedfiles.append(str(filestomerge[0])+'_merged')
			mergedfiles.append(str(filestomerge[1])+'_merged')
		else:
			return(files)
		
		HKout = []
		SCout = []
		self.progress.setRange(0,round(len(filestomerge)/2))
		self.progress.setValue(0)
		for i in range(round(len(filestomerge)/2)):
			with open(filestomerge[round(2*i)],"rb") as infile:
				HKheader = np.fromfile(infile,np.int32,7)
				try: numHK = HKheader[0]
				except: continue
				HKraw = np.fromfile(infile,np.int32)
			with open(filestomerge[round(2*i)+1],"rb") as infile:
				SCheader = np.fromfile(infile,np.int32,8)
				try: numSC = SCheader[0]
				except: continue
				SCraw = np.fromfile(infile,np.int32)
			ctLineHK = numHK + 2
			nrecsHK = len(HKraw) / float(ctLineHK)

			ctLineSC = numSC + 2
			nrecsSC = len(SCraw) / float(ctLineSC)

			HKraw = HKraw[:math.floor(nrecsHK)*ctLineHK+1]
			SCraw = SCraw[:math.floor(nrecsSC)*ctLineSC+1]

			if i == 0:	
				with open(mergedfiles[0],'wb') as outfile:
					outfile.write(HKheader)
					HKraw.tofile(outfile)
				with open(mergedfiles[1],'wb') as outfile:
					outfile.write(SCheader)
					SCraw.tofile(outfile)
			else:
				with open(mergedfiles[0],'ab') as outfile:
					HKraw.tofile(outfile)
				with open(mergedfiles[1],'ab') as outfile:
					SCraw.tofile(outfile)
			self.progress.setValue(i+1)
			#self.progress.setValue((i+1)*int(100/round(len(filestomerge)/2)))
		return(mergedfiles)
	
	def readHK(self,file, saveCSV=False):
		with open(file,"rb") as infile:
			numHK = (np.fromfile(infile,np.int32,1))[0]
			tmparray = (np.fromfile(infile,np.float32,4))
			MFCset = tmparray[0]
			vStart = tmparray[1]
			vEnd = tmparray[2]
			vMod = tmparray[3]
			tmparray = (np.fromfile(infile,np.int32,2))
			pp2fEnable = tmparray[0]
			minsPerFile = tmparray[1]
			HKraw = (np.fromfile(infile,np.int32))
			
		ctLine = round(numHK + 2)
		nrecs = math.floor(len(HKraw) / float(ctLine))

		HKraw = HKraw[:math.floor(nrecs)*ctLine]

		HKraw = np.reshape(HKraw,(nrecs,ctLine))#(ctLine,nrecs))

		if self.timeSpanExtract.isChecked():
			startText = self.startTime.text()
			endText = self.endTime.text()
	
			startTime = gcal2jd(startText[0:4],startText[4:6],startText[6:8])[1]*86400 + int(startText[9:11])*60*60 + int(startText[11:13])*60 + int(startText[13:15])
			endTime = gcal2jd(endText[0:4],endText[4:6],endText[6:8])[1]*86400 + int(endText[9:11])*60*60 + int(endText[11:13])*60 + int(endText[13:15])
			
			startTime = startTime - gcal2jd(1970,1,1)[1]*86400
			endTime = endTime - gcal2jd(1970,1,1)[1]*86400
	
			validTimes = np.where(np.logical_and(np.greater_equal(np.array(HKraw[:,0]),startTime),np.less_equal(np.array(HKraw[:,0]),endTime)))
			nrecs = len(validTimes[0]);
			HKraw = HKraw[validTimes[0],:]

		seconds = np.array(HKraw[:,0])

		microseconds = np.array(HKraw[:,1])#,:]
		HKdata = 5.0*(HKraw[:,2:]/32767)#,:]+32767)/65535
		#HKdata = 5.0*(HKraw[:,2:]+32767)/65535#,:]+32767)/65535

		jd = np.array([0.0 for x in seconds])
		offset = gcal2jd(1970,1,1)[0]+gcal2jd(1970,1,1)[1]
		for i in range(nrecs):
			jd[i] = offset + seconds[i]/(60*60*24) + (microseconds[i]*(1e-6))/86400

		#temps = ((HKdata[:,3:6]**2)*137.68-HKdata[:,3:6]*498.74+387.8)
		#temps[:,2] = temps[:,2]+2.0

		temps = ((HKdata[:,3:6]))

		press = HKdata[:,6]*290.22 - 3.3685

		MFC = HKdata[:,11]*2.0

		current = HKdata[:,10]

		if saveCSV:	
			with open(file+'.csv', 'wb') as csvfile:
				datestring = ''.join(''.join(''.join(str(file).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
				datestring = ''.join(datestring.split('_')[0])
				seconds = np.round((jd - 
					gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[0]-
					gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[1])*86400 + 1)
						
				#np.savetxt(csvfile, np.c_[seconds+microseconds*1e-6,HKdata],fmt = '%.6f',delimiter = ',', newline = '\r\n', header = 'seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC')
				np.savetxt(csvfile, np.c_[seconds+microseconds*1e-6,HKdata[:,:3],temps,press,current,HKdata[:,8],MFC],fmt = '%.6f',delimiter = ',', newline = '\r\n', header = 'seconds, pd, tdetect, tlaser, temp1, tbody, temp2, press, current, vlaser, MFC')

		HK = {'juldate':jd,
			'PD':HKdata[:,0],
			'tdetect':HKdata[:,1],
			'tlaser':HKdata[:,2],
			'temp1':temps[:,0],
			'tbody':temps[:,1],
			'temp2':temps[:,2],
			'press':press,
			'current':current,
			'vlaser':HKdata[:,8],
			'MFC':MFC }

		return HK
		#plt.plot(jd, HKdata[:,3])#)#[:,0])		
		#plt.show()

	def readSC(self,file, saveCSV = False):
		with open(file,"rb") as infile:
			numSC = (np.fromfile(infile,np.int32,1))[0]
			numDark = (np.fromfile(infile,np.int32,1))[0]
			tmparray = (np.fromfile(infile,np.float32,4))
			MFCset = tmparray[0]
			vStart = tmparray[1]
			vEnd = tmparray[2]
			vMod = tmparray[3]
			tmparray = (np.fromfile(infile,np.int32,2))
			pp2fEnable = tmparray[0]
			minsPerFile = tmparray[1]
			SCraw = (np.fromfile(infile,np.int32))
		
		ctLine = round(numSC + 2)
		nrecs = math.floor(len(SCraw) / float(ctLine))
		
		SCraw = SCraw[:math.floor(nrecs)*ctLine]

		SCraw = np.reshape(SCraw,(nrecs,ctLine))#(ctLine,nrecs))

		if self.timeSpanExtract.isChecked():
			startText = self.startTime.text()
			endText = self.endTime.text()
	
			startTime = gcal2jd(startText[0:4],startText[4:6],startText[6:8])[1]*86400 + int(startText[9:11])*60*60 + int(startText[11:13])*60 + int(startText[13:15])
			endTime = gcal2jd(endText[0:4],endText[4:6],endText[6:8])[1]*86400 + int(endText[9:11])*60*60 + int(endText[11:13])*60 + int(endText[13:15])
			
			startTime = startTime - gcal2jd(1970,1,1)[1]*86400
			endTime = endTime - gcal2jd(1970,1,1)[1]*86400
	
			validTimes = np.where(np.logical_and(np.greater_equal(np.array(SCraw[:,0]),startTime),np.less_equal(np.array(SCraw[:,0]),endTime)))
			nrecs = len(validTimes[0])
			SCraw = SCraw[validTimes[0],:]
	
		seconds = np.array(SCraw[:,0])#,:]
		microseconds = np.array(SCraw[:,1])#,:]
		SCdata = 10.0*(SCraw[:,2:])/65535.0#,:]+32767)/65535

		jd = np.array([0.0 for x in seconds])
		offset = gcal2jd(1970,1,1)[0]+gcal2jd(1970,1,1)[1]
		for i in range(nrecs):
			jd[i] = offset + seconds[i]/(60*60*24) + (microseconds[i]*(1e-6))/86400
		
		if saveCSV:	
			with open(file+'.csv', 'wb') as csvfile:
				#np.savetxt(csvfile, 'hello')
				datestring = ''.join(''.join(''.join(str(file).split('/')[-1:]).split('CLH2-')[-1:]).split('_')[0])
				datestring = ''.join(datestring.split('_')[0])
				seconds = np.round((jd - 
					gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[0]-
					gcal2jd((datestring[0:4]),(datestring[4:6]),(datestring[6:8]))[1])*86400 + 1)
				
				np.savetxt(csvfile, np.arange(1024).reshape(1,np.arange(1024).shape[0]), fmt = '%d', delimiter = ',',  newline = '\r\n')
				np.savetxt(csvfile, np.c_[seconds+microseconds*1e-6,SCdata],fmt = '%.6f',delimiter = ',', newline = '\r\n')
		
		SC = {'juldate':jd,
			'scans':SCdata }
		#plt.plot(np.arange(numSC), SC['scans'][0,:])#)#[:,0])		
		#plt.show()
		return SC

	def fixjuldate(self,input):
		output = input
		seconds = (input - math.floor(input[0])+0.5)*3600*24
		leftptr = 1
		flagptr = 1
		rightptr = len(input)
		obs = len(input) - 1
		for i in range(obs):
			delta = seconds[i]-seconds[i-1]
			if delta <= 0:
				flagptr = i
			if delta>=2 or i==len(input)-2:
				rightptr = i
				if flagptr>1:
					correction = output[flagptr]-output[flagptr-1]
					correction-= (output[rightptr-1]-output[flagptr])/(rightptr-flagptr+1)
					output[leftptr-1:flagptr-1] = output[leftptr-1:flagptr-1]+correction
				leftptr = i+1
				rightptr = i+1

		return output	

	def averageonehz(self,HK,SC):
		seconds = (SC['juldate'] - math.floor(SC['juldate'][0])+0.5)*3600*24
		start = math.ceil(min(seconds))
		stop = math.floor(max(seconds))

		nsteps = stop-start+1
		secsOut = start+np.arange(nsteps)
		juldate = secsOut/(3600*24)-0.5+float(math.floor(SC['juldate'][0]))
		
		[hist,histval] = np.array(np.histogram(seconds,np.arange(start,stop+2)))
		dims = SC['scans'].shape
		scanint = np.zeros((len(hist),dims[1]))

		tmparray = [math.floor(x) for x in seconds]
		tmp, un_ind = np.unique(tmparray, return_index = True)

		#Returns a true/false mask of length of first arg if elements are in 
		histmask = np.in1d(histval, tmp)

		j = 0
		mask = []
		for i in range(len(histval)):
			if not histmask[i]:# or j >= len(tmp): 
				mask.append(0)
				continue
			while True:
				if histval[i] == tmp[j]: 
					mask.append(un_ind[j])
					break
				else: j+=1
					 
		self.progress.setRange(0,nsteps)
		self.progress.setValue(0)	
		for i in range(0,nsteps):
			if hist[i] == 0: scanint[i,:] = math.nan
			elif hist[i] == 1: scanint[i,:] = histval[i]
			else:

				#IF CODE BREAKS USE THE FOLLOWING
				#indices = np.where(tmparray == histval[i])
				#scanint[i,:] = np.mean(SC['scans'][indices],0)
				#if histmask[i]: scanint[i,:] = SC['scans'][mask[i]]
				if histmask[i]:	scanint[i,:] = np.mean(SC['scans'][mask[i]:mask[i]+hist[i]],0)

				self.progress.setValue(i+1)		


		missing = [i for i, val in enumerate(scanint[:,0]) if not np.isfinite(val)]

		HK['PD'] = np.interp(juldate,HK['juldate'],HK['PD'])
		HK['tdetect'] = np.interp(juldate,HK['juldate'],HK['tdetect'])
		HK['tlaser'] = np.interp(juldate,HK['juldate'],HK['tlaser'])
		HK['temp1'] = np.interp(juldate,HK['juldate'],HK['temp1'])
		HK['tbody'] = np.interp(juldate,HK['juldate'],HK['tbody'])
		HK['temp2'] = np.interp(juldate,HK['juldate'],HK['temp2'])
		HK['press'] = np.interp(juldate,HK['juldate'],HK['press'])
		HK['current'] = np.interp(juldate,HK['juldate'],HK['current'])
		HK['vlaser'] = np.interp(juldate,HK['juldate'],HK['vlaser'])
		HK['MFC'] = np.interp(juldate,HK['juldate'],HK['MFC'])
				

		if(len(missing) > 0):
			HK['PD'][missing] = -9999
			HK['tdetect'][missing] = -9999
			HK['tlaser'][missing] = -9999
			HK['temp1'][missing] = -9999
			HK['tbody'][missing] = -9999
			HK['temp2'][missing] = -9999
			HK['press'][missing] = -9999
			HK['current'][missing] = -9999
			HK['vlaser'][missing] = -9999
			HK['MFC'][missing] = -9999

		SC['juldate'] = np.array(juldate)
		SC['scans'] = scanint

		HK['juldate'] = np.array(juldate)
		
		return [HK,SC]



	def lineint(self,scans,numDark,plotscans,fitlen,press,celltemp,figdir):
		dims = scans.shape
		obs = dims[0]
		scanpts = dims[1]
		
		x = np.arange(scanpts)
		powerzero = np.mean(scans[:,2:numDark+1],1)
		
		lower1 = numDark
		lower2 = numDark+fitlen+1
		upper1 = round(scanpts-fitlen*0.75)
		upper2 = scanpts

		intvmr = np.arange(float(obs))
		centerindex = np.arange(obs)
		vscan = np.arange(scanpts)

		#ims = []
		#self.figure.clear()
		#ax = self.figure.add_subplot(111)
		#line1, line2, = ax.plot(x,scans[0,:],'k',x,scans[0,:],'r')
		
		self.progress.setRange(0,obs)
		self.progress.setValue(0)	
		for i in range(obs):
			scanact = -np.abs((scans[i,:]) - powerzero[i])
			yarr = np.r_[scanact[lower1:lower2],scanact[upper1:upper2]]
			xarr = np.r_[x[lower1:lower2],x[upper1:upper2]]
			fitout = np.polyfit(xarr,yarr,3)
			fitline = fitout[3] + fitout[2]*x + fitout[1]*x**2 + fitout[0]*x**3
			scanfit = scanact - fitline
			#valid = [i for i, val in enumerate(x) if val > lower1]

			valid = np.where(x > lower1)
			#print(valid)

			maxindex = np.argmin(scanfit[valid])

			#maxindex+=lower1
			power = fitline[maxindex]
			powervo = scanact[maxindex]
			scanscale = scanact/fitline

			centerindex[i] = maxindex + lower1 + 1

			try:	intvmr[i] = (np.trapz(1.0 - scanscale[valid],x=vscan[valid]))
			except:	intvmr[i] = -9999

			#print(intvmr[i])

			#line1.set_xdata(xarr)
			#line1.set_ydata(yarr)
			#line2.set_xdata(xarr)
			#line2.set_ydata(yarr)
			#line1.set_ydata(1.0-scanscale)
			#line2.set_ydata(1.0-scanscale)

			#ax.relim()
			#ax.autoscale_view()
			#ims.append([line1,line2])
			#self.canvas.draw()			

			self.progress.setValue(i+1)		

		powermax = (-1)*np.min(scans,1)
		#print(powermax.shape)
		#March 2013 cal
		fitted = np.array([-8.0605e3, -7.1624e0, -7.0584e3, -6.3956e0, -9.0851e-2, 1.0054e-1, 2.4235e-4])
	
		#October cal1
		#fitted = np.array([1.78e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])
		#October cal2
		#fitted = np.array([9e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])
	
		fitted = np.array([9.9882e4, -6.3415e3, 2.113e3, 1.3178e1, -6.0409e-2, 6.2395e-2, 1.6877e-4, -1.04886e5])	
	
		VMR = (fitted[0]+fitted[1]*press + fitted[2]*intvmr + fitted[3]*press*intvmr)/(1+fitted[4]*press + fitted[5]*intvmr + fitted[6]*press*intvmr) + fitted[7]
		#VMR = (fitted[0]+fitted[1]*press + fitted[2]*intvmr + fitted[3]*press*intvmr)/(1+fitted[4]*press + fitted[5]*intvmr + fitted[6]*press*intvmr)
				
		#powerzero = np.mean(scans[:,4:35],1)
		#print(powerzero.shape)

		ints = {'dark':powerzero,
			'int':intvmr,
			'VMR':VMR,
			'powermax':powermax,
			'centerindex':centerindex}		
			#'leftend':np.arange(float(obs)),		
			#'rightend':np.arange(float(obs)),		
			#'peakval':np.arange(float(obs)),		
			#'fwhm':np.arange(float(obs)),		
			#'newVMR':np.arange(float(obs)),		
			#'a':np.arange(float(obs)),		
			#'b':np.arange(float(obs)),		
			#'c':np.arange(float(obs)),
			#'d':np.arange(float(obs))}		

		return ints

	#
	# Define your function to calculate the residuals.
	# The fitting function holds your parameter values.
	#
	def residuals(self, p, y, x):
		err = y - self.back(x, p)
		return err

	def spectralResiduals(self, p, y, x):
		err = y - self.pval(x,p)
		return err

	def pval(self, x, p):
		varx = (p[0]-x)/(p[1]/2)
		gauss = np.exp(-np.log(2)*varx**2)
		lorentz = 1/(1+varx**2)
		convolution = p[2] * (p[3]*gauss + (1-p[3])*lorentz)
		background = p[4] + p[5]*x + p[6]*x**2 + p[7]*x**3
		final = np.exp(-convolution)*background
		return final

	def back(self, x, p):
		background = p[0] + p[1]*x + p[2]*x**2 + p[3]*x**3
		return background
	'''
	def convolve(self, arr, kernel):
		#Simple convolution of two arrays
		npts = min(len(arr), len(kernel))
		pad = np.ones(npts)
		tmp = np.concatenate((pad*arr[0], arr, pad*arr[-1]))
		out = np.convolve(tmp, kernel, mode = 'valid')
		noff = int((len(out) - npts)/2)
		return out[noff:noff+npts]
	'''
	def exponent(self, arr, kernel):
		#print(1.0*np.exp(kernel))
		#return 1.0*np.exp(-1.0 * arr) #Used for speeding up fits (bad data)
		return 1.0*np.exp(-1.0 * kernel)

	def voigt(self, x, amplitude = 1.0, center = 0.0, sigma = 1.0, gamma = None):
		s2pi = sqrt(2*pi)
		s2 = sqrt(2.0)
		if gamma is None:
			gamma = sigma
		z = (x-center + 1j*gamma) / (sigma*s2)
		return amplitude*wofz(z).real / (sigma*s2pi)

	def domShift(self, pars, x):
		vals = pars.valuesdict()
		c = 0.0
		for i in range(self.wvlngthOrder.value()+1):
			c = c + vals['shift_c'+str(i)]*x**i
		return c
		
	def domShiftInv(self, pars, x):#Inverted
		vals = pars.valuesdict()
		c = []
		for i in range(self.wvlngthOrder.value()+1):
			c.append(vals['shift_c'+str(i)])
		if len(c) == 2:
			return (x - c[0])/c[1]
		if len(c) == 3:
			result = (np.sqrt(-4*c[0]*c[2] + 4*c[2]*x + c[1]**2) - c[1])/(2*c[2])
			if result > 0 and result < 1024: return result# and not any(np.isnan(result)): return result
			else: return (-np.sqrt(-4*c[0]*c[2] + 4*c[2]*x + c[1]**2) - c[1])/(2*c[2])
		if len(c) >= 4:
			return (1/(81*np.cbrt(2)*c[3]))*((np.sqrt((-531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**2 + 4*(2187*c[1]*c[3] - 729*c[2]**2)**3) - 531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**(1/3)) - (np.cbrt(2)*(2187*c[1]*c[3] - 729*c[2]**2)) / (81*c[3]*(np.sqrt((-531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**2 + 4*(2187*c[1]*c[3] - 729*c[2]**2)**3) - 531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**(1/3)) - c[2]/(3*c[3])

	def laserBackground(self, pars, x):
		vals = pars.valuesdict()
		p = 0.0
		for i in range(self.backOrder.value()+1):
			p = p + vals['back_c' + str(i)]*x**i
		return p

	def spectralModel(self, pars, x, raw = False, prefix = None, data = None):
		s2pi = sqrt(2*pi)
		s2 = sqrt(2.0)
		#model = np.zeros(len(x), dtype = 'float')

		vals = pars.valuesdict()
		y = x#self.domShift(pars, x)
		if not raw: y = self.domShift(pars,x)
	
		if prefix is None:
			lines = range(self.numLines.value())
		else: lines = range(prefix,prefix+1)
	


		for i in lines:
			amp = vals['voigt'+str(i)+'_amplitude']
			cen = vals['voigt'+str(i)+'_center']
			sig = vals['voigt'+str(i)+'_sigma']
			gam = vals['voigt'+str(i)+'_gamma']

			if i > 0:
				sig = vals['voigt0_sigma']*vals['voigt'+str(i)+'_sigma']
				gam = vals['voigt0_gamma']*vals['voigt'+str(i)+'_gamma']
				amp = vals['voigt0_amplitude']*vals['voigt'+str(i)+'_amplitude']

			if gam is None:
				gam = sig
			z = (y-cen + 1j*gam) / (sig*s2pi)
			try:	model = model + amp*wofz(z).real / (sig*s2pi)
			except:	model = amp*wofz(z).real / (sig*s2pi)

		if not raw:
			background = self.laserBackground(pars, x)
			model = exp(-model)*background

		if data is None:	return model
		return (model - data)

	'''	
	def _wofz(x):
		#Returns the fadeeva function for complex argument
		#wofz = exp(-x**2)*erfc(-i*x)
		return wofz(x)

	def _erfc(x):
		#Return the complementary error function.
		#erfc = 1 - erf(x)
		return erfc(x)

	def _erf(x):
		#Returns the error function.
		#erf = 2/sqrt(pi)*integral(exp(-t**2), t = [0,z])
		return erf(x)
	'''

	def linefits(self,ints,HK,scans,numDark, polyorder, numlines, wvlngthorder):
		dims = scans.shape
		obs = dims[0]
		scanpts = dims[1]
	
		#SCANS[observation, points]
	
		x = np.arange(scanpts)
		absscans = np.abs(scans)

		powerzero = np.mean(scans[:,4:35],1)
		for i in range(obs):
			scans[i,:] = scans[i,:] - powerzero[i]

		scans = absscans	
		
		scans = scans/50.0	
		#self.upscale = 10
		#For normalizing the spectra to account for various coadds
		
		fitparams = {}
		for i in range(wvlngthorder+1):
			fitparams['shift_c'+str(i)] = np.zeros(obs)
		
		HK['normScale'] = HK['press']*0.0

		for i in range(obs):
			HK['normScale'][i] = np.linalg.norm(scans[i,:])		
			scans[i,:] = scans[i,:]/np.linalg.norm(scans[i,:])

		#print(HK['normScale'])
		#input('wait')
		
		self.upscale = 1
		scans = scans*self.upscale

		bestfits = scans*0.0
		
		left = numDark+50
		right = 10
		#160 offset seemed to work for some
		#75 from each end seems to be the sweet spot
		

		lineset = 0
		if self.timeMenu.currentIndex() in range(14):
			lineset = 0
			left = numDark+35
			right = 75
			numlines = 4
			self.numLines.setValue(4)
		elif self.timeMenu.currentIndex() in [14,17,18,21,22,25,26,29,30,33,34,37,38]:
			lineset = 2
			left = numDark+100 #just past a little line on the left
			right = 75
			numlines = 3
			self.numLines.setValue(3)
		else: #This is for the proxy
			lineset = 1
			left = numDark+50
			right = 5
			numlines = 3
			self.numLines.setValue(3)
	
		if lineset == 0:
			lCenter = np.array([467,715,503,558])
			wvlngths = np.array([2647.542486, 2647.673962, 2647.565197, 2647.594939])
			isonum = np.array([11, 14, 12, 12])
			mags = np.array([4.28e-23, 1.63e-23, 7.58e-24, 1.33e-24])
			molMass = np.array([18, 19, 20, 20])
			mags = mags*1e20#*self.upscale #worked with e21
		if lineset == 1:
			#Proxy
			lCenter = np.array([812, 514, 321])#, 0])
			wvlngths = np.array([1372.736978, 1372.675119, 1372.636458])
			isnum = np.array([11,11,11])
			mags = np.array([1.01e-22, 1.98e-23, 3.67e-24])
			mags = mags*1e19#*self.upscale #worked with e20
			airWid = np.array([0.0722, 0.083, 0.051])
			selfWid = np.array([0.35, 0.493, 0.275])
			tempDep = np.array([0.61, 0.71, 0.51])
			molMass = np.array([18,18,18])
		elif lineset == 2:
			#1.3um real
			lCenter = np.array([460, 724, 819, 187, 0])
			wvlngths = np.array([1372.485618, 1372.538469, 1372.557915, 1372.425142, 1372.490702, 1372.557116])
			isonum = np.array([11, 12, 11, 12, 11, 11])
			mags = np.array([2.05e-22, 3.44e-23, 2.36e-24, 1.71e-24, 2.10e-24, 6.70e-25])
			mags = np.array([2.071e-22, 2.36e-23, 3.03e-24, 1.71e-24])
			mags = mags*1e20
			molMass = ([18, 20, 18, 20, 18, 18])
		#sigma_D = wv#/(c)*sqrt(2*Na*k*T*ln(2)/M) #result in units of 1/cm
		dopplerWidth = ((10000000)/(wvlngths*299792458))*np.sqrt(2*6.02214129*1.38064852*(23+273.15)*np.log(2)/(18/1000)) 
	
		wvlngths = 10000000/wvlngths

		wvScale = 1
		wvOffset = 0#np.floor(min(wvlngths))
		wvlngths = wvScale*(wvlngths - wvOffset)

		p0 = np.array([0, 0, 0, 0])
		xarr = np.r_[x[numDark+5:left],x[-2*right:-right]]
		yarr = np.r_[scans[0,numDark+5:left],scans[0,-2*right:-right]]
		
		back_mod = PolynomialModel(polyorder,prefix = 'back_')
		pars = back_mod.guess(yarr,x=xarr)
		back_guess = [0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		for i in range(polyorder+1):
			pars['back_c'+str(i)].set(value = back_guess[i])

		background = back_mod.fit(yarr, pars, x=xarr)

		#set_ydata(out.eval_components(x=x[left:-right])['voigt0_'])
		#plt.plot(x,scans[0,:],'k',xarr,background.best_fit,'b')

		#deriv = np.gradient(np.gradient(testscan))
		'''
		vsin = np.zeros(len(scans[0,:]))
		vcos = np.zeros(len(scans[0,:]))	

		for i in range(len(scans[0,:])):
			vsin[i] = (np.sin(2*(i)*np.pi*(1/16)))
			vcos[i] = (np.cos(2*(i)*np.pi*(1/16)))

		b,a = butter(3, (scanpts/90)/(0.5*scanpts), btype = 'low', analog = False)
		'''
		#struct.__dict__ lists attributes
		plsq = []
		for i in range(polyorder+1):
			plsq.append(background.params['back_c'+str(i)].value)

		v_mod = VoigtModel(prefix = 'voigt0_')
		for i in range(numlines-1):
			v_mod = CompositeModel(v_mod, VoigtModel(prefix = 'voigt'+str(i+1)+'_'), np.add)

		mod = CompositeModel(ConstantModel(),v_mod,self.exponent)
		mod = CompositeModel(mod, PolynomialModel(polyorder, prefix = 'back_'), np.multiply)

		#pars = mod.make_params()#guess(scans[0,left:],x=x[left:])

		#pars['c'].set(value = 1.0, vary = False)

		#for i in range(polyorder+1):		
		#	pars['back_c'+str(i)].set(value = plsq[i],min = -10, max = 10)
		#butter(order, cutoff)
		b,a = butter(2, (scanpts/75)/(0.5*scanpts), btype = 'low', analog = False)
		testscan = scans[0,:]
		testscan[:numDark+10] = background.eval_components(x=x[:numDark+10])['back_'] + testscan[numDark+10] - background.eval_components(x=x[numDark+10])['back_']

		testscan = filtfilt(b,a,testscan[numDark+10:])
		testscan = np.r_[np.zeros(numDark+10),testscan]
		testscan[:numDark+10] = testscan[numDark+11]

		deriv = np.gradient(np.gradient(testscan))
		deriv = deriv[left:-right]

		for i in range(len(deriv)-1):
			try:
				if deriv[i] > deriv[i+1]: continue
				else:
					deriv[:i] = deriv[i+1]
					break
			except: break

		for i in range(len(deriv)-1):
			try:
				if deriv[-i-1] > deriv[-i-2]: continue
				else:
					deriv[-i-1:] = deriv[-i-2]
					break
			except: break
		testscan = testscan[left:-right]

		newderiv = deriv

		backSlope = float(np.abs((scans[0,-right] - scans[0,left])/(x[-right]-x[left])))
		backIntercept = float(scans[0,left] - backSlope*x[left])
		backArr = [backIntercept, backSlope, 0, 1.0e-12]
		#backMins = [-self.upscale/10, 0, -1]
		#backMaxs = [self.upscale, self.upscale/1000, 1]
		backMins = [backIntercept - 0.05*self.upscale, backSlope*0.85, -1.0e-8*self.upscale, -1.0e-10]
		backMaxs = [backIntercept + 0.05*self.upscale, backSlope*1.2, 1.0e-8*self.upscale, 1.0e-10]
		backMins = [-np.inf, -np.inf, -np.inf]
		backMaxs = [np.inf, np.inf, np.inf]	
	
		pars = Parameters()
		
		for i in range(polyorder+1):
			pars.add('back_c'+str(i), max = backMaxs[i], min = backMins[i], value = backArr[i])#plsq[i])		


		shiftSlope = -np.abs((max(wvlngths[:numlines]) - min(wvlngths[:numlines]))/(max(lCenter[:numlines])-min(lCenter[:numlines])))
		#shiftSlope /= 2

		#shiftIntercept = min(wvlngths[:numlines]) - shiftSlope*min(lCenter[:numlines])
		shiftIntercept = (wvlngths[0]) - shiftSlope*(lCenter[0])
		shiftIntercept += (wvlngths[numlines-1] - shiftSlope*(lCenter[numlines-1]))
		shiftIntercept /= 2

		shiftArr = [shiftIntercept, shiftSlope, 0, 1.0e-12]

		#shiftMins = [min(wvlngths[:numlines]) - 1, shiftSlope*0.75, -1e-5]
		#shiftMaxs = [min(wvlngths[:numlines]), shiftSlope*1.5, 1e-5]#1/1000, 1]
		shiftVar = max(wvlngths) - min(wvlngths)
		#print(shiftVar)
		if lineset == 0: 
			shiftVar *= 1
		else: 
			shiftVar *= 0.5
		#input('wait')
		shiftMins = [shiftIntercept - shiftVar*wvScale, shiftSlope*0.5, -1e-6*wvScale, -1.0e-9]
		shiftMaxs = [shiftIntercept + shiftVar*wvScale, shiftSlope*2.0, 1e-6*wvScale, 1.0e-9]
		
		if lineset == 0:
			#shiftIntercept = 3777.309
			#shiftSlope = -0.00028#39716#0.0002
			shiftArr = [shiftIntercept, shiftSlope, 0.0, 1e-9]
			shiftMins = [shiftIntercept - shiftVar*wvScale, shiftSlope*0.9, -1e-7*wvScale, -1.0e-9]
			shiftMaxs = [shiftIntercept + shiftVar*wvScale, shiftSlope*1.1, 1e-7*wvScale, 1.0e-9]
		#shiftMins = [shiftIntercept - 100, shiftSlope*1.05, -1e-6, -1.0e-9]
		#shiftMaxs = [np.inf, shiftSlope*0.95, 1e-6, 1.0e-9]
		
		#shiftMins = [shiftIntercept*.9, shiftSlope*0.8, -5e-5, -np.inf]
		#shiftMaxs = [shiftIntercept*1.1, shiftSlope*1.25, 5e-5, np.inf]
	
		#shiftMins = [-np.inf, -np.inf, -np.inf, -np.inf]
		#shiftMaxs = [np.inf, np.inf, np.inf, np.inf]

		#pars.add('shift_c0', value = 2647.294908, min = 2646.294908, max = 2647.294908, vary = True)
		#pars.add('shift_c1', value = 0.00053, min = 0.00042, max = 0.00066, vary = True)
		#pars.add('shift_c2', value = 1e-8, min = -1e-5, max = 1e-5, vary = True)
		for i in range(wvlngthorder+1):
			pars.add('shift_c'+str(i), value = shiftArr[i], min = shiftMins[i], max = shiftMaxs[i], vary = True)
		
		for line in range(numlines):
			pars.add('voigt'+str(line)+'_center', value = wvlngths[line], vary = False)
			if line == 0:
				if lineset == 0:
					pars.add('voigt'+str(line)+'_amplitude', value = 1e-3, min = 0, max = .1, vary = True)
					pars.add('voigt'+str(line)+'_sigma', value = 0.002*wvScale, min = 7e-6, max = 7e-3*wvScale, vary = True)
					pars.add('voigt'+str(line)+'_gamma', value = 0.03*wvScale, min = 1e-3, max= .1*wvScale, vary = True)
				else:
					pars.add('voigt'+str(line)+'_amplitude', value = 5e-3*wvScale, min = 0, max = 1*wvScale, vary = True)
					pars.add('voigt'+str(line)+'_sigma', value = 0.004*wvScale, min = 1e-3, max = 6e-3*wvScale, vary = True)
					pars.add('voigt'+str(line)+'_gamma', value = 0.03*wvScale, min = 9e-8, max= 1*wvScale, vary = True)
				#pars['voigt'+str(line)+'_amplitude'].set(value = mags[line], min = 0, max = .1, vary = True)
				#pars.add('voigt'+str(line)+'_amplitude'].set(value = mags[line], min = 0, max = 1, vary = True)
			if line == 1:#line > 0 and line < 4:
				#Sigma ~ gamma/pressure * 50
				#Gamma scales directly with pressure,
				# 	i.e. gamma ~ 0.00576 at P ~ 386, then at P ~ 193, it will be half (using O18, O16 pair as example) 
				#Initial sig,gam guesses worked reasonably well with 0.01, changing to much smaller
				#For 1.3 um, gamma should be ~ 0.006
				#For 2.6 um, gamma follows same relation; however, is ~ .02168 at ~374 mbar, so should be 0.023187
				#Gamma is exactly 4 times larger at 2.6um.
				if lineset == 0:
					pars.add('voigt'+str(line)+'_gamma', value = 1.00, min = 0.5, max = 1.5, vary = True)
					pars.add('voigt'+str(line)+'_amplitude', value = mags[line]/mags[0], min = 0.3*mags[line]/mags[0], max = 1.5*mags[line]/mags[0], vary = True) 
				else:
					pars.add('voigt'+str(line)+'_gamma', value = 1.00, min = 0.1, max = 2.0, vary = True)
					pars.add('voigt'+str(line)+'_amplitude', value = mags[line]/mags[0], min = 0.6*mags[line]/mags[0], max = 2.0*mags[line]/mags[0], vary = True) 
				pars.add('voigt'+str(line)+'_sigma', value = (wvlngths[0]/wvlngths[line])*np.sqrt(molMass[0]/molMass[line]), min = 1e-5, max = 1e2, vary = False)
			if line == 2:
				if lineset == 0:
					pars.add('voigt'+str(line)+'_sigma', value = (wvlngths[0]/wvlngths[line])*np.sqrt(molMass[0]/molMass[line]), vary = False)
					pars.add('voigt'+str(line)+'_gamma', value = 1.0, min = 0.75, max = 1.25, vary = False)
					pars.add('voigt'+str(line)+'_amplitude', value = mags[line]/mags[0], min = 0.0*mags[line]/mags[0], max = 1.1*mags[line]/mags[0], vary = True)
				else:
					pars.add('voigt'+str(line)+'_sigma', value = (wvlngths[0]/wvlngths[line])*np.sqrt(molMass[0]/molMass[line]), vary = False)
					pars.add('voigt'+str(line)+'_gamma', value = 1.0, min = 0.5, max = 2.0, vary = False)
					pars.add('voigt'+str(line)+'_amplitude', value = mags[line]/mags[0], min = 0.0*mags[line]/mags[0], max = 1.1*mags[line]/mags[0], vary = True)
			if line == 3:
				pars.add('voigt'+str(line)+'_sigma', value = (wvlngths[0]/wvlngths[line])*np.sqrt(molMass[0]/molMass[line]), vary = False)
				pars.add('voigt'+str(line)+'_gamma', value = 1.0, vary = False)
				pars.add('voigt'+str(line)+'_amplitude', value = mags[line]/mags[0], min = 0.0*mags[line]/mags[0], max = 3.0*mags[line]/mags[0], vary = True)
		
		#for line in range(numlines):
		#	if np.max(newderiv) >= 0:#np.std(deriv):
		#		centerguess = np.argmax(newderiv)
		#		print(centerguess+left)
		#		for i in range(centerguess,0,-1):
		#			if newderiv[i] < 0:
		#				fwhmguess = centerguess - i
		#				sigmaguess = fwhmguess/3.6013
		#				newderiv[i:centerguess] = 0
		#				break
		#		#for i in range(centerguess,scanpts):
		#		for i in range(centerguess,len(newderiv)):
		#			if newderiv[i] < 0:
		#				newderiv[centerguess:i] = 0
		#				break
		ims = []
		self.figure.clear()
		#ax = self.figure.add_subplot(231)
		#ax.plot(CLHtime,ints['VMR'],'k')
		
		nullSpectra = zeros(len(x[left:-right]),dtype='float')
	
		ax = self.figure.add_subplot(111)
		line1, line2, line3, line4, line5, line6, line7, = ax.plot(x[left:-right],nullSpectra,'k',x[left:-right],nullSpectra,'r',
			x[left:-right],nullSpectra,'b',x[left:-right],nullSpectra,'y',
			x[left:-right],nullSpectra,'g',x[left:-right],nullSpectra,'m',
			x[left:-right],nullSpectra,'c')
	
		self.progress.setRange(0,obs)

		extraLineParams = ['_integral','_pointwise']
		extraParams = ['chisqr','redchi','ndata','nvarys', 'nfev','success','ier','aic','bic']

		#fitparams = {}
		for i in range(wvlngthorder+1):
			fitparams['shift_c'+str(i)] = np.zeros(obs)
		for i in range(polyorder+1):
			fitparams['back_c'+str(i)] = np.zeros(obs)
		for i in range(numlines):
			fitparams['voigt'+str(i)+'_center'] = np.zeros(obs)
			fitparams['voigt'+str(i)+'_amplitude'] = np.zeros(obs)
			fitparams['voigt'+str(i)+'_sigma'] = np.zeros(obs)
			fitparams['voigt'+str(i)+'_gamma'] = np.zeros(obs)
			#fitparams['voigt'+str(i)+'_fwhm'] = np.zeros(obs)
			#fitparams['voigt'+str(i)+'_height'] = np.zeros(obs)
			for vals in extraLineParams:
				fitparams['voigt'+str(i)+vals] = np.zeros(obs)
		for i in range(numlines-1):
			fitparams['del'+str(i)] = np.zeros(obs)
		for vals in extraParams:
			fitparams[vals] = np.zeros(obs)


		wideDomain = np.arange(-scanpts, 2*scanpts, 1/10)

		back_mod_1 = PolynomialModel(polyorder,prefix = 'back_')
		back_pars_1 = back_mod.guess(yarr,x=xarr)
		back_guess_1 = [0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		for i in range(polyorder+1):
			back_pars_1['back_c'+str(i)].set(value = back_guess_1[i], vary = True)
		
		rc = np.zeros(numlines,dtype='int')
		abs_max = np.zeros(numlines)
		for i in range(obs):
			#try:
			for vals in range(numlines):
				#pars['voigt'+str(vals)+'_amplitude'].set(value = out.params['voigt'+str(vals)+'_amplitude'].value, vary = True)	
				if vals == 0:
					#pars['voigt'+str(vals)+'_amplitude'].set(value = 1e-3)#1e-4)
					if lineset > 0:
						#pars['voigt'+str(vals)+'_gamma'].set(value = 0.007*HK['press'][i]/400)#For wavelength
						pars['voigt'+str(vals)+'_gamma'].set(value = 0.031*HK['press'][i]/400*wvScale)#For wavenumber
					else:
						#pars['voigt'+str(vals)+'_gamma'].set(value = 4*0.0065*HK['press'][i]/400)#For wavelength
						pars['voigt'+str(vals)+'_gamma'].set(value = 0.032*HK['press'][i]/400*wvScale)#For wavenumber
					#print(HK['press'][i])
					#pars['voigt'+str(vals)+'_sigma'].set(value = pars['voigt0_gamma']/HK['press'][i]*10)#*50)#For wavelength
					#pars['voigt'+str(vals)+'_sigma'].set(value = 0.003)#*50)#For wavenumber
				if vals > 0:
					pars['voigt'+str(vals)+'_amplitude'].set(value = mags[vals]/mags[0])
					#pars['voigt'+str(vals)+'_sigma'].set(value = 1)
					#pars['voigt'+str(vals)+'_gamma'].set(value = 1)
			try:
				#print(pars)
				self.progress.setValue(i+1)				
				out = minimize(self.spectralModel, pars, args = (x[left:-right],), kws = {'data':scans[i,left:-right]}, scale_covar = True)
				#out.params.pretty_print()
				print(fit_report(out))
				#print(shiftMins)
				#print(shiftMaxs)
				#input('wait')
				#print("Chi Squared Result: ",out.chisqr)
				print("Doppler Width: ",dopplerWidth)	
				for j in range(numlines):
					abs_max[j] = max(self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,j))

				scaling = max(scans[i,left:-right]) / max(abs_max)
				
				line1.set_ydata(self.spectralModel(out.params,x[left:-right]))
				line2.set_ydata(scans[i,left:-right])
			
				bestfits[i,:] = self.spectralModel(out.params, x)
	
				line3.set_ydata(self.laserBackground(out.params,x[left:-right]))
				line4.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,0))

				if numlines > 1: line5.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,1))
				if numlines > 2: line6.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,2))
				if numlines > 3: line7.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,3))

				ax.relim()
				ax.autoscale_view()

				if numlines == 1: ims.append([line1,line2,line3,line4])
				if numlines == 2: ims.append([line1,line2,line3,line4,line5])
				if numlines == 3: ims.append([line1,line2,line3,line4,line5,line6])
				if numlines == 4: ims.append([line1,line2,line3,line4,line5,line6,line7])

				self.canvas.draw()			
				app.processEvents()
			

				for key, value in fitparams.items():
					find = False
					for val in extraLineParams+extraParams+['del']:
						if val in key: find = True
					if not find: 
						fitparams[key][i] = out.params[key].value
						if out.params[key].value == pars[key].value and out.params[key].vary : input("warning: failure to iterate value: "+key)
						if out.params[key] <= pars[key].min + (pars[key].max - pars[key].min)/10000 and out.params[key].vary and 'shift_c1' not in key: input("warning: value pinned to min: "+key)
						if out.params[key] >= pars[key].max - (pars[key].max - pars[key].min)/10000 and out.params[key].vary and 'shift_c1' not in key: input("warning: value pinned to max: "+key)
						#print(out.params[key].value)
					find = False

					#if not any(x in key for x in (['del']+extraLineParams + extraParams)): 
					#	print(key)
					#	fitparams[key][i] = vars(out)[key]

				for key in extraParams:
					fitparams[key][i] = vars(out)[key]

				for vals in range(1, numlines):
					fitparams['voigt'+str(vals)+'_amplitude'][i] *= fitparams['voigt0_amplitude'][i]
					fitparams['voigt'+str(vals)+'_gamma'][i] *= fitparams['voigt0_gamma'][i]
					fitparams['voigt'+str(vals)+'_sigma'][i] *= fitparams['voigt0_sigma'][i]

				a = []
				for vals in range(numlines):
					fitparams['voigt'+str(vals)+'_center'][i] = self.domShiftInv(out.params,fitparams['voigt'+str(vals)+'_center'][i])
					a.append(fitparams['voigt'+str(vals)+'_center'][i])	
				print('centers: ', a)
				#input('wait')	
				a = []
				for vals in range(numlines):
					fitparams['voigt'+str(vals)+'_integral'][i] = integrate.quad(lambda z: self.spectralModel(out.params, z, True, vals), wvlngths[vals]-2, wvlngths[vals]+2)[0]
					a.append(fitparams['voigt'+str(vals)+'_integral'][i])
				print('integrals: ',a)
		
				for vals in range(numlines - 1):
					fitparams['del'+str(vals)][i] = fitparams['voigt'+str(vals+1)+'_integral'][i]/fitparams['voigt'+str(vals)+'_integral'][i]
	
				for vals in range(wvlngthorder+1):
					pars['shift_c'+str(vals)].set(value = out.params['shift_c'+str(vals)].value)
	
				for vals in range(polyorder+1):
					pars['back_c'+str(vals)].set(value = out.params['back_c'+str(vals)].value)
					#print(fitparams['voigt'+str(vals)+'_integral'][i])
				
				for vals in range(numlines):
					#if not np.isnan(out.params['voigt'+str(vals)+'_amplitude']):
					pars['voigt'+str(vals)+'_amplitude'].set(value = out.params['voigt'+str(vals)+'_amplitude'].value)	
					pars['voigt'+str(vals)+'_gamma'].set(value = out.params['voigt'+str(vals)+'_gamma'].value)
					pars['voigt'+str(vals)+'_sigma'].set(value = out.params['voigt'+str(vals)+'_sigma'].value)
				
				#for vals in range(1, numlines):
				#	if not np.isnan(out.params['voigt'+str(vals)+'_amplitude']):
				#		pars['voigt'+str(vals)+'_amplitude'].set(value = out.params['voigt'+str(vals)+'_amplitude'].value)	
					#if not np.isnan(out.params['voigt'+str(vals)+'_sigma']):
					#	pars['voigt'+str(vals)+'_sigma'].set(value = out.params['voigt'+str(vals)+'_sigma'].value)
				
				background_1 = back_mod_1.fit(yarr, back_pars_1, x=xarr)
				abs_spectrum = (1-scans[i,:]/background_1.eval_components(x=x)['back_'])
				for j in range(numlines):
					rc[j] = int(np.argmax(abs_spectrum[lCenter[j]-20:lCenter[j]+20])+lCenter[j]-20)
					fitparams['voigt'+str(j)+'_pointwise'][i] = (np.mean(abs_spectrum[rc[j]-20:rc[j]+20]))	
					
			except BaseException as e:
				print(e)
				print('error in fitting')
				for key, value in fitparams.items():
					fitparams[key][i] = -9999
				#ints['newVMR'][i] = -9999
				#continue
				#pass
				sys.exit(app.exec_())
				#return

	
		try:	
			animationSaveFile = self.basepath.split('.dat')[0] + '.mp4'
			ani = animation.ArtistAnimation(self.figure, ims,
				interval = 20, blit = True)
			
			Writer = animation.writers['ffmpeg']
			Writer = animation.FFMpegWriter()
			writer = Writer(fps = 50, metadata = dict(artist = 'Me'), bitrate = 1800)
			ani.save(animationSaveFile, writer = writer)
			self.canvas.draw()
		except: pass

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
				
			#outData = np.c_[daysecs, HK['PD'], HK['tdetect'], HK['tlaser'], HK['temp1'], HK['tbody'], HK['temp2'], HK['press'], HK['current'], HK['vlaser'], HK['MFC'], ints['int'], ints['VMR'], ints['dark'], ints['centerindex']]#, ints['newVMR']]
			outData = np.c_[self.seconds]
		
			for key in hkarray:
				try: outData = np.c_[outData, HK[key]]
				except: pass			

			for key in fitarray:
				try: outData = np.c_[outData, fitparams[key]]
				except: pass#outData = np.c_[outData, HK[key]]

			#for key, value in HK.items():
			#	outData = np.c_[outData, HK[key]]
			
			#if fitparams != -9999:
				#for key in fitarray:
				#	outData = np.c_[outData, fitparams[key]]
			#	for key, value in fitparams.items():
			#		outData = np.c_[outData, fitparams[key]]

			for row in outData:
				tmp = '{:11d}'.format(int(row[0]))+','
				row = row[1:]
				#tmp+=','.join(["{:11.6f}".format(x) for x in row])
				tmp+=','.join(["{:.6E}".format(x) for x in row])
				tmp+='\r\n'
				outfile.write(tmp)

		#for i in range(obs):
		#	scans[i] = scans[i]*HK['normScale'][i]/self.upscale
		#	bestfits[i] = bestfits[i]*HK['normScale'][i]/self.upscale

		with open(self.basepath.split('.dat')[0]+'_rawSpectra'+'.csv', 'wb') as csvfile:
			np.savetxt(csvfile, np.arange(-1,1024).reshape(1,np.arange(-1,1024).shape[0]), fmt = '%d', delimiter = ',',  newline = '\r\n')
			np.savetxt(csvfile, np.c_[self.seconds,scans],fmt = '%.6E',delimiter = ',', newline = '\r\n')

		with open(self.basepath.split('.dat')[0]+'_fitSpectra'+'.csv', 'wb') as csvfile:
			np.savetxt(csvfile, np.arange(-1,1024).reshape(1,np.arange(-1,1024).shape[0]), fmt = '%d', delimiter = ',', newline = '\r\n')
			np.savetxt(csvfile, np.c_[self.seconds,bestfits],fmt = '%.6E',delimiter = ',', newline = '\r\n')

		#plt.plot(x[50:],scans[0,50:],'k',x[50:],mod.eval(pars,x=x[50:]),'r')
		#plt.plot(x[left:],comps['voigt_'],'k',x[left:],scans[0,left:]/comps['back_'],'r')
		#out options:
		# best_fit, init_fit, 

		#plt.plot(x[left:], scans[0,left:], 'k', x[left:], out.best_fit, 'r')		
		#plt.plot(x[left:], out.residual)
		#plt.show()
		#print(fitparams)

		return fitparams
	#def init(self):
	#	return self.ln,

	def update(self,x,frame):
		self.xdata.append(np.arange(len(frame)))
		self.ydata.append(frame)
		self.ln.set_data(xdata,ydata)
		return self.ln,

	def saveText(self,HK,ints,fitparams,outName):
		timestamp = time.strftime("%Y%m%d")
		outName = (''.join(outName.split('packaged_')[:-1])+'packaged_'+str(timestamp)+'.txt')
		datestring = ''.join(''.join(outName.split('CLH2-')[-1:]).split('_')[0])
		dateout = str(datestring[0:4])+', '+str(datestring[4:6])+', '+str(datestring[6:8])+', '+str(timestamp[0:4])+', '+str(timestamp[4:6])+', '+str(timestamp[6:8])	

		with open(outName,'w') as outfile:
			outfile.writelines('45, 1001\r\n')
			outfile.write('Toohey, Darin\r\n')
			outfile.write('University of Colorado\r\n')
			outfile.write('Total water concentration from tunable diode laser infrared spectrometer measurements of water vapor resulting from condensed water particle vaporization in heated inlet. inlet - NCAR GV HIAPER\r\n')
			outfile.write('ORCAS\r\n')
			outfile.write('1,1\r\n')
			outfile.write(dateout+'\r\n')
			outfile.write('1.0\r\n')
			outfile.write('Start_UTC, seconds, seconds since start of day of record\r\n')
			outfile.write('14\r\n')
			outfile.write('1,1,1,1,1,1,1,1,1,1,1,1,1,1\r\n')
			outfile.write('-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999\r\n')
			outfile.write('PD, Monitor photodiode, volts\r\n')
			outfile.write('Tdetect, Detector temperature, volts\r\n')
			outfile.write('Tlaser, Laser temperature, volts\r\n')
			outfile.write('Tcell, Cell temperature #1, degrees_C\r\n')
			outfile.write('Tbody, Instrument baseplace temperature, degrees_C\r\n')
			outfile.write('Pcell, Cell pressure, mb\r\n')
			outfile.write('Claser, Laser current, amps\r\n')
			outfile.write('Vlaser, Laser voltage, volts\r\n')
			outfile.write('MFC, Cell mass flow rate, sLm^-1\r\n')
			outfile.write('AbInt, bsorption feature integral, integrated_volts\r\n')
			outfile.write('VMR, Calibrated VMR, ppmv\r\n')
			outfile.write('Dark, Laser dark counts, ADC counts\r\n')
			outfile.write('IndexMax, Index of line center within scan, scan steps\r\n')
			outfile.write('0\r\n')
			outfile.write('17\r\n')
			outfile.write('PI_CONTACT_INFO: Darin Toohey; Department of Atmospheric and Oceanic Sciences; University of Colorado at Boulder; darin.toohey@colorado.edu; (303) 735-0002\r\n')
			outfile.write('PLATFORM: NCAR GV - sampling from canister on left outboard canister\r\n')
			outfile.write('LOCATION: Aircraft location data available from https://www.eol.ucar.edu/projects/orcas/data.html\r\n')
			outfile.write('ASSOCIATED_DATA: see http://www.eol.ucar.edu/projects/dc3/data.html\r\n')
			outfile.write('INSTRUMENT_INFO: CLH Total Water - Tunable diode laser hygrometer sampling through anisokinetic heated inlet.\r\n')
			outfile.write('UNCERTAINTY: Formal error estimate not yet available.\r\n')
			outfile.write('ULOD_FLAG: -7777\r\n')
			outfile.write('ULOD_VALUE: 30000\r\n')
			outfile.write('LLOD_FLAG: -8888\r\n')
			outfile.write('LLOD_VALUE: N/A\r\n')
			outfile.write('DM_CONTACT_INFO: NCAR EOL Data Manager\r\n')
			outfile.write('PROJECT_INFO: ORCAS Mission 13 January - 27 February 2016; based in Punta Arenas, Chile.\r\n')
			outfile.write('STIPULATIONS_ON_USE: \r\n')
			outfile.write('OTHER_COMMENTS: N/A\r\n')
			outfile.write('REVISION: R0\r\n')
			outfile.write('R0: Quicklook estimates\r\n')

			headerstring = 'UTC_Start, PD, Tdetect, Tlaser, Tcell, Tbody, Tcell2, Pcell, Claser, Vlaser, MFC, AbInt, VMR, Dark, IndexMax'
			if fitparams != -9999:
				fitarray = []
				for key, value in fitparams.items():
					fitarray.append(key)
					#headerstring += ', '
					#headerstring += str(key)
				fitarray = np.sort(fitarray)
				headerstring+= ', '
				headerstring+= ', '.join(fitarray)
			headerstring+= '\r\n'
			outfile.write(headerstring)

			#outfile.write('UTC_Start, PD, Tdetect, Tlaser, Tcell, Tbody, Tcell2, Pcell, Claser, Vlaser, MFC, AbInt, VMR, Dark, IndexMax\r\n')

			daysecs = np.round((HK['juldate'] - gcal2jd(datestring[0:4],datestring[4:6],datestring[6:8])[0] - gcal2jd(datestring[0:4],datestring[4:6],datestring[6:8])[1])*86400)
	
			daysecs = np.array(daysecs)

			outData = np.c_[daysecs, HK['PD'], HK['tdetect'], HK['tlaser'], HK['temp1'], HK['tbody'], HK['temp2'], HK['press'], HK['current'], HK['vlaser'], HK['MFC'], ints['int'], ints['VMR'], ints['dark'], ints['centerindex']]#, ints['newVMR']]
			if fitparams != -9999:
				for key in fitarray:
					outData = np.c_[outData, fitparams[key]]
				#for key, value in fitparams.items():
				#	outData = np.c_[outData, value]

			for row in outData:
				tmp = '{:11d}'.format(int(row[0]))+','
				row = row[1:]
				tmp+=','.join(["{:11.6f}".format(x) for x in row])
				tmp+='\r\n'
				outfile.write(tmp)
		return daysecs



	def plotResults(self,CLHtime,HK,SC,ints):
		#plt.figure(1)
	
		self.figure.clear()

		ax = self.figure.add_subplot(231)
		ax.plot(CLHtime,ints['VMR'],'k')
		ax.set_title('VMR observation')
		ax.set_xlabel('Seconds')		
		ax.set_ylabel('VMR (ppmv)')

		ax = self.figure.add_subplot(232)
		ax.plot(CLHtime,HK['temp1'],'k',CLHtime,HK['temp2'],'r',CLHtime,HK['tbody'],'b')
		ax.set_title('Cell (bk, r) and body (blu) temps')
		ax.set_xlabel('Seconds')
		ax.set_ylabel('Temperature (degC)')

		ax = self.figure.add_subplot(233)
		ax.plot(CLHtime,HK['press'],'k')
		ax.set_title('Pressure')
		ax.set_xlabel('Seconds')
		ax.set_ylabel('Pressure (mb)')
	
		ax = self.figure.add_subplot(234)
		ax.plot(CLHtime,HK['MFC'],'k')
		ax.set_title('Mass flow rate')
		ax.set_xlabel('Seconds')
		ax.set_ylabel('MFC (sLm)')

		ax = self.figure.add_subplot(235)
		ax.plot(CLHtime,HK['tlaser'],'r',CLHtime,HK['tdetect'],'k')
		ax.set_title('Laser (r) and Detector (bk) Temp')
		ax.set_xlabel('Seconds')
		ax.set_ylabel('Temperature (raw voltage)')
	
		ax = self.figure.add_subplot(236)
		ax.plot(np.arange(len(SC['scans'][0,:])),SC['scans'][round(len(ints['VMR'])/2),:],'k')
		ax.set_title('Sample scan')
		ax.set_xlabel('sample')
		ax.set_ylabel('Scan Units (cts)')

		#ax.set_subplots_adjust(top=0.92, bottom=0.08, left = 0.10, right = 0.95, hspace = 0.25, wspace = 0.35)

		self.figure.tight_layout(pad = 0.1, w_pad = 0.1, h_pad = 0.1)

		self.canvas.draw()

		#plt.show()	
		#plt.plot(np.arange(numSC), SC['scans'][0,:])#)#[:,0])		
		#plt.show()

	
	def openFileNamesDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		#files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Python Files (*.py)", options = options)
		files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "/mnt/c/Users/rainw/Desktop/github/CLH2/python/Test/", "All Files (*);;Python Files (*.py)", options = options)
		#	print(files)
		if files:
			return(files)
		else: return(False)

	def closeEvent(self, event):
		result = QMessageBox.warning(MainWindow, 'WARNING',"Are you sure you want to close the program?", QMessageBox.Yes, QMessageBox.No)
		event.ignore()

		if result == QMessageBox.Yes:
			event.accept()


if __name__ == '__main__':
	#app = QtWidgets.QApplication(sys.argv)
	#MainWindow = MyWindow()
	#ui = Ui_MainWindow()
	#ui.initUI(MainWindow)
	#MainWindow.showMaximized()	
	#sys.exit(app.exec_())

	app = QApplication(sys.argv)
	MainWindow = Ui_MainWindow()
	MainWindow.setWindowTitle("CLH2 Extraction Program")
	MainWindow.showMaximized()

	sys.exit(app.exec_())


