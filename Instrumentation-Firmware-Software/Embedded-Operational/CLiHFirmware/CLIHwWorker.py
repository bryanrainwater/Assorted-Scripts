import numpy as np
import time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

import datetime as dt
import timeit
import csv
import fastcsv as fastcsv

import pyqtgraph as pg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import copy
from copy import deepcopy
from pylab import *
	
from ctypes import *
dsm = CDLL('./dsm.so')

#import dsm
#dsm = CDLL.LoadLibrary('./dsm.so')

class Ui_MainWindow(QWidget):
   saveSignal = pyqtSignal(object,object,object)
   tempChange = pyqtSignal(object,object)

   def __init__(self, parent=None):
      super(Ui_MainWindow, self).__init__(parent)
      self.title = 'Isotope Instrument'
      self.left = 20
      self.top = 50
      #self.width = 960*1.8
      #self.height = 540*1.7
      self.width = 960*1
      self.height = 540*1.1
      self.initUI()

   def initUI(self):
      #Widget adds are in form y,x,ylen,xlen

      #Configure dimensions and style
      self.setWindowTitle(self.title)
      self.setGeometry(self.left, self.top, self.width, self.height)
      QApplication.setFont(QtGui.QFont("Times",10,QtGui.QFont.Bold))
      self.setStyleSheet("""QMainWindow{background-color: rgb(0,0,100);}""")

      #Configure layout and tabs
      xdiv = 32 #Used to force alignment to grid
      #mainWidget = QtWidgets.QWidget()
      mainLayout = QtWidgets.QGridLayout(self)#mainWidget)
      
      tabWidget = QtWidgets.QTabWidget()#mainWidget)
      tabWidget.setStyleSheet("""QTabWidget{background-color: rgb(220,220,255);}""")

      tab1 = QtWidgets.QWidget(tabWidget)
      tabWidget.addTab(tab1,"Main")
      tab1Layout = QtWidgets.QGridLayout(tab1)

      tab2 = QtWidgets.QWidget(tabWidget)
      tabWidget.addTab(tab2,"Configuration")
      tab2Layout = QtWidgets.QGridLayout(tab2)
      
      self.startBtn = QPushButton("Start")
      tab1Layout.addWidget(self.startBtn,0,0,1,int(xdiv/2))
      self.startBtn.clicked.connect(self.beginScans)

      self.stopBtn = QPushButton("Stop")
      tab1Layout.addWidget(self.stopBtn,0,int(xdiv/2),1,int(xdiv/2))
      self.stopBtn.clicked.connect(self.dsmStop)

      #self.figure = plt.figure(tight_layout=True)
      #self.canvas = FigureCanvas(self.figure)
      self.plot = pg.PlotWidget() 
      #self.toolbar = NavigationToolbar(self.canvas,self)
      
      #tab1Layout.addWidget(self.plot,1,0,1,xdiv)
      tab1Layout.addWidget(self.plot,1,int(xdiv/4),20,3*int(xdiv/4))
      #self.layout.addWidget(self.toolbar,1,0,1,2)
      #self.layout.addWidget(self.canvas,2,0,1,2)
      self.plot.show()
      self.plot.setTitle("Spectral Traces",color='w')
      self.plot.setLabel('bottom',text = 'Bit Number')
      self.plot.setLabel('left',text = 'Voltage (V)')

      self.plot2 = pg.ViewBox()
      self.plot.scene().addItem(self.plot2)
      self.plot.getAxis('right').linkToView(self.plot2)
      self.plot2.setXLink(self.plot)

      self.plot.getAxis('left').setPen(\
         pg.mkPen(color=(255,255,255), width=3))
      self.plot.getAxis('bottom').setPen(\
         pg.mkPen(color=(255,255,255), width=3))
      self.plot.getAxis('right').setPen(\
         pg.mkPen(color=(255,125,125), width=3))


      #C = pg.hsvColor(time.time()/5%1,alpha=0.5)
      #pen = pg.mkPen(color=C,width=10)
      #self.plotDataItem = self.plot.plot([])
      
      #self.plotItem = pg.GraphicsWindow.addPlot(title="Spectrum"
      #self.plotDataItem = self.plot.plot([],pen=pen,symbolBrush=(255,0,0),symbolSize=2,symbolPen=None)
      #self.plot.plot([],pen=pen,clear=True,symbolBrush=(255,0,0),symbolSize=2,symbolPen=None)

      self.wvScanConfig = {}
      self.wvScanConfig['startTemp'] = 11.0
      self.wvScanConfig['endTemp'] = 25.0
      self.wvScanConfig['tempSteps'] = 29
      self.wvScanConfig['settleTime'] = 9#15 #in seconds
      self.wvScanConfig['avgPerStep'] = 2000#2000#5000


      self.dsmConfig = {}#\
      self.dsmConfig['bufferSize'] = 2048
      self.dsmConfig['numADChan'] = 2#1
      self.dsmConfig['numDAChan'] = 2#1
      self.dsmConfig['laserNum'] = 0
      self.dsmConfig['outRate'] = 160000
      self.dsmConfig['saveRate'] = 1.0#2.0
      self.dsmConfig['lPstart'] = 30
      self.dsmConfig['lPend'] = 100
      self.dsmConfig['dark'] = 10#5
      
      self.dsmConfig['l1Temp'] = 21.8
      self.dsmConfig['l2Temp'] = 21.6#20.0
      self.dsmConfig['setMFC'] = 0.5

      self.dsmConfig['laserTuning'] = 0#False
      self.dsmConfig['spectralScan'] = False
      if self.dsmConfig['laserTuning']:
         self.dsmConfig['numADChan'] = 2
         self.dsmConfig['numDAChan'] = 2
         self.dsmConfig['outRate'] = 6000
      

      fileTime = self.getDateTime("%Y%m%d_%H%M")#%S") 

      self.fileConfig = {}
      self.fileConfig['basePath'] = '/home/dscguest/CLIHPython/'
      self.fileConfig['HK'] = 'Data/CLIH-'+fileTime+'_HK.csv'
      self.fileConfig['SC'] = 'Data/CLIH-'+fileTime+'_SC.csv'
      self.fileConfig['fullScan'] = '' 
      self.fileConfig['logFile'] = 'startLog.txt'
      self.fileConfig['configFile'] = 'configFile.txt'




      #Mode options:::::
      tmp = QLabel('Mode of Operation')
      tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      tab1Layout.addWidget(tmp,1, 0,1,int(xdiv/4))
      tmp = QRadioButton("Laser 1 Only")
      tmp.setChecked(True)
      tab1Layout.addWidget(tmp,2, 0,1,int(xdiv/4))
      tmp.setObjectName('lmode0')
      tmp.toggled.connect(lambda: \
         self.confUpdate('lmode0'))
      tmp = QRadioButton("Laser 2 Only")
      tab1Layout.addWidget(tmp,3, 0,1,int(xdiv/4))
      tmp.setObjectName('lmode1')
      tmp.toggled.connect(lambda: \
         self.confUpdate('lmode1'))
      tmp = QRadioButton("Both Lasers")
      tab1Layout.addWidget(tmp,4, 0,1,int(xdiv/4))
      tmp.setObjectName('lmode2')
      tmp.toggled.connect(lambda:\
         self.confUpdate('lmode2'))

      #Configurations
      tmp = QLabel('Configuration Options')
      tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      tab1Layout.addWidget(tmp,5, 0,1,int(xdiv/4))

      confOptions = ['Buffer Size','Data Rate (Hz)','Save Rate (Hz)','Start Power (mW)', 'End Power (mW)', 'Dark Window (%)']
      #initialVals = [2048,150000,2.0,40,120,10]
      initialVals = [self.dsmConfig['bufferSize'],self.dsmConfig['outRate'],\
         self.dsmConfig['saveRate'],self.dsmConfig['lPstart'],\
         self.dsmConfig['lPend'],self.dsmConfig['dark']]
      bounds = [[128,2048],[1,250000],[1/100,50],[20,100],[0,100],[0,100]]
      for i, (conf,init,bnds) in enumerate(zip(confOptions,initialVals,bounds)):
         tmp = QLabel(conf)
         tab1Layout.addWidget(tmp,6+i,0,1,int(xdiv/8))
         if i!=2: tmp = QSpinBox()
         else: tmp = QDoubleSpinBox()
         tmp.setMinimum(bnds[0])
         tmp.setMaximum(bnds[1])
         tmp.setValue(init)
         tmp.setKeyboardTracking(False)
         tab1Layout.addWidget(tmp,6+i,5*int(xdiv/32),1,3*int(xdiv/32))
         tmp.setObjectName('option'+str(i))
         tmp.valueChanged.connect(lambda new,i=i: \
            self.confUpdate('option'+str(i)))

      tmp = QPushButton("Run Temperature Scans")
      tab1Layout.addWidget(tmp,12,0,1,int(xdiv/4))
      tmp.setObjectName('tempScan')
      tmp.setCheckable(True)
      tmp.clicked.connect(lambda: self.runTempScans(False))

      tmp = QPushButton("RE-INITIALIZE DSM")
      tab1Layout.addWidget(tmp,13,0,1,int(xdiv/4))
      tmp.clicked.connect(self.dsmReinit)

      tmp = QLabel("AVG CTR")
      tab1Layout.addWidget(tmp,14,0,1,int(xdiv/8))
      tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      tmp = QLabel("LOSS CTR")
      tab1Layout.addWidget(tmp,14,int(xdiv/8),1,int(xdiv/8))
      tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

      tmp = QLineEdit("NA")
      tab1Layout.addWidget(tmp,15,0,1,int(xdiv/8))
      tmp.setObjectName("avgCtr")
      tmp.setDisabled(True)
      tmp = QLineEdit("NA")
      tab1Layout.addWidget(tmp,15,int(xdiv/8),1,int(xdiv/8))
      tmp.setObjectName("lossCtr")
      tmp.setDisabled(True)



      cntrlOffset = 21

      mpeADChans = ['L1Temp','L2Temp','Temp','Press']#3,4]
      mpeDAChans = ['L1Temp','L2Temp','MFC','N/A']
      mpeDAMax = [25.0,25.0,5.0,5.0]
      mpeDAInitials = [self.dsmConfig['l1Temp'],self.dsmConfig['l2Temp'],\
         0.5, self.dsmConfig['setMFC']]
      mpeDAMin = [5.0,5.0,0.0,0]
      self.mpeDAScale = [10,10,100,100]
      for i,(ADchan,DAchan,DAmin,DAmax,DAscale,DAinit) in enumerate(zip(mpeADChans,mpeDAChans,mpeDAMin,mpeDAMax,self.mpeDAScale,mpeDAInitials)):
         tmp = QLabel('Chan '+str(i)+': '+str(ADchan))
         tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
         tab1Layout.addWidget(tmp,cntrlOffset + 2, int(xdiv/4*(i)),1,int(xdiv/8))
         tmp = QLineEdit()
         tmp.setDisabled(True)
         tab1Layout.addWidget(tmp,\
            cntrlOffset + 2,int(xdiv/8*(i*2+1)),1,int(xdiv/8))
         tmp.setObjectName('mpeAD'+str(i))

         tmp = QFrame()
         tmp.setFrameShape(QFrame.HLine)
         tab1Layout.addWidget(tmp,cntrlOffset + 3,0,1,xdiv)

         tmp = QLabel('Cntrl '+str(i)+': '+str(DAchan))
         tmp.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
         tab1Layout.addWidget(tmp,cntrlOffset + 4, int(xdiv/4*(i)),1,int(xdiv/8))
         tmp = QDoubleSpinBox()
         tmp.setMinimum(DAmin)
         tmp.setMaximum(DAmax)
         tmp.setValue(DAinit)
         tab1Layout.addWidget(tmp,\
            cntrlOffset + 4,int(xdiv/8*(i*2+1)),1,int(xdiv/8))
         tmp.setObjectName('mpespinbox'+str(i))
         tmp.setKeyboardTracking(False)
         tmp.valueChanged.connect(lambda new,i=i: \
            self.cntrlUpdate('mpespinbox'+str(i)))

         tmp = QSlider(Qt.Horizontal,tab1)
         tmp.setMinimum(int(DAmin*DAscale))
         tmp.setMaximum(int(DAmax*DAscale))
         tmp.setValue(DAinit*DAscale)
         tmp.setTickPosition(QSlider.TicksBelow)
         tmp.setTickInterval(1*DAscale)
         tab1Layout.addWidget(tmp,\
            cntrlOffset + 5,int(xdiv/4*(i)),1,int(xdiv/4)) 
         tmp.setObjectName('mpeslider'+str(i))
         tmp.valueChanged.connect(lambda new,i=i: \
            self.cntrlUpdate('mpeslider'+str(i)))

         #tmp = QPainter()
         #pen = QPen(Qt.black,2,Qt.SolidLine)
         #pen.setStyle(Qt.DashLine)
         #tmp.drawLine(3,0,1,xdiv)
         #tab1Layout.addWidget(tmp)#,3,0,1,xdiv) 
      #tab1Layout.addWidget(QFrame.HLine),5,0,1,xdiv)

      #self.setLayout(self.layout)






      #self.figure.clear()
      #self.ax = self.figure.subplots()
      #self.ax.set_xlabel('Domain')
      #self.ax.set_ylabel('Range')
      #self.ax.set_title('WhyDoINeedATitle')

      #app.processEvents()
      #time.sleep(5)

      #self.dsmInit()

      mainLayout.addWidget(tabWidget,0,0,1,1)
      self.dsmInit()
      #.setCentralWidget(mainWidget)


      self.saveSignal.connect(self.dataSave)
      self.tempChange.connect(self.tempChangeFromThread)


      #self.dsmThread = DSMLoop(self.dsmConfig,self.wvScanConfig)
      #Line above is for using strictly QThread
      #Lines below are for linking to QWorker

      self.workerLink = QThread()
      self.workerLink.start()
      self.dsmThread = DSMLoop(self.dsmConfig,self.wvScanConfig)
      self.dsmThread.moveToThread(self.workerLink)
      #self.dsmThread.start.connect(self.dsmThread.run)
      #self.dsmThread.stop.connect(self.dsmThread.stop)
       



      #Is this necessary?
      #QtCore.QMetaObject.connectSlotsByName(self)#window)
   
   def runTempScans(self, stop = False):
      self.dsmConfig['spectralScan'] = True
      tmp = self.findChild(QPushButton,'tempScan')

      if stop:
         #tmp.setText("Run Temperature Scans")
         #tmp.setDisabled(False)
         tmp.setChecked(False)
         self.dsmStop()
         self.dsmConfig['spectralScan'] = False
      else:
         #tmp.setDisabled(True)  
         self.fileConfig['fullScanHeader'] = []
         self.fileConfig['fullScanHeader'].append(\
            ['#Temperature Scanning Spectral File'])
         self.fileConfig['fullScanHeader'].append(\
            ['Time (sec)', 'Time (usec)', '#Scans Avgd',\
            'Temp','Settle Time', 'lPstart', 'lPend','dataRate',\
            'dark','Chan0', 'Chan1', 'Chan2', 'Chan3',\
            'Chan4', 'Chan5', 'Chan6', 'Chan7', 'Scans -> '])
 
         fileTime = self.getDateTime("%Y%m%d_%H%M%S")#%S") 
         self.fileConfig['fullScan'] = 'TEMPSCAN-'+fileTime+'.csv'
         
         self.fullScanFile = open(self.fileConfig['basePath']+\
            self.fileConfig['fullScan'],'w',newline='')
         for row in self.fileConfig['fullScanHeader']:
            csv.writer(self.fullScanFile).writerow(row)
         

         #if ~self.dsmThread.isRunning():
         if self.dsmThread.stopFlag:#isRunning():
            self.beginScans()
         else: self.dsmReinit()


   def tempChangeFromThread(self,chan = 0, temp = 25.0):
      #print("Temperature is being changed from thread?") 
      self.findChild(QDoubleSpinBox,'mpespinbox'+str(chan)).\
         setValue(temp)

   def getDateTime(self, fmt = "%Y%m%d%H%M"):
      now = dt.datetime.now()
      return now.strftime(fmt)

   def confUpdate(self,toggle = ''):
      if toggle == '': return
      if 'option' in toggle: 
         self.dsmConfig['bufferSize'] = \
            int(self.findChild(QSpinBox,'option0').value())
         #self.dsmConfig['numADChan'] = 1
         #self.dsmConfig['numDAChan'] = 1
         self.dsmConfig['outRate'] = \
            int(self.findChild(QSpinBox,'option1').value())
         self.dsmConfig['saveRate'] = \
            float(self.findChild(QDoubleSpinBox,'option2').value())
         self.dsmConfig['lPstart'] = \
            int(self.findChild(QSpinBox,'option3').value())
         self.dsmConfig['lPend'] = \
            int(self.findChild(QSpinBox,'option4').value())
         self.dsmConfig['dark'] = \
            int(self.findChild(QSpinBox,'option5').value())
    
      if 'lmode' in toggle:
         for i in range(3):
            self.findChild(QRadioButton,'lmode'+str(i)).\
               blockSignals(True)
            #self.findChild(QRadioButton,'lmode'+str(i)).\
            #   disconnect()
            self.findChild(QRadioButton,'lmode'+str(i)).\
               setChecked(False)
         
         self.findChild(QRadioButton,toggle).setChecked(True)
         
         lNum = int(toggle[-1])
         if lNum <= 1:
            self.dsmConfig['laserNum'] = lNum
            self.dsmConfig['numDAChan'] = 1
            self.dsmConfig['numADChan'] = 1
         else:
            self.dsmConfig['laserNum'] = 0
            self.dsmConfig['numDAChan'] = 2
            self.dsmConfig['numADChan'] = 2   
         
         for i in range(3):
            self.findChild(QRadioButton,'lmode'+str(i)).\
               blockSignals(False)
            #self.findChild(QRadioButton,'lmode'+str(i)).\
            #   toggled.connect(lambda new, i=i: self.confUpdate('lmode'+str(i)))
  
      #Run script for reconfiguring DSM options:::
      self.dsmReinit()
      #if self.dsmThread.isRunning():#self.dsmTimer.isActive():
      #   self.dsmThread.stop()#
      #   #self.dsmStop() 
               

   def cntrlUpdate(self,toggle = ''):
      if toggle == '': return
      if 'spinbox' in toggle:
         self.findChild(QtWidgets.QSlider,'mpeslider'+toggle[-1]).\
            blockSignals(True)
         self.findChild(QtWidgets.QSlider,'mpeslider'+toggle[-1]).\
            setValue(int(self.findChild(QtWidgets.QDoubleSpinBox,toggle).\
            value()*self.mpeDAScale[int(toggle[-1])]))
         self.findChild(QtWidgets.QSlider,'mpeslider'+toggle[-1]).\
            blockSignals(False)
      if 'slider' in toggle:
         self.findChild(QtWidgets.QDoubleSpinBox,'mpespinbox'+toggle[-1]).\
            blockSignals(True)
         self.findChild(QtWidgets.QDoubleSpinBox,'mpespinbox'+toggle[-1]).\
            setValue(self.findChild(QtWidgets.QSlider,toggle).\
            value()/self.mpeDAScale[int(toggle[-1])])
         self.findChild(QtWidgets.QDoubleSpinBox,'mpespinbox'+toggle[-1]).\
            blockSignals(True)
      if 'spinbox' in toggle or 'slider' in toggle:
         tmp = self.findChild(QtWidgets.QDoubleSpinBox,'mpespinbox'\
            +toggle[-1]).value()
         if int(toggle[-1]) < 2:
            self.setLaserTemp(int(toggle[-1])+1, tmp)
         else:
            dsm.writeMPEvoltage(c_float(tmp), int(toggle[-1]))


   def dsmReinit(self):
      #print('Reinitializing DSM')
      #wasActive = self.dsmThread.isRunning()#self.dsmTimer.isActive()
      wasActive = ~self.dsmThread.stopFlag#isRunning()#self.dsmTimer.isActive()
      if wasActive:
         self.dsmThread.stop()
         #self.dsmThread.stop.emit()
         #self.dsmStop()
      
      dsm.interface_close()
      app.processEvents()
      self.dsmInit()

      if wasActive:
         self.dsmThread.dsmConfig = self.dsmConfig
         self.dsmThread.wvScanConfig = self.wvScanConfig
         #self.dsmThread.start()#priority = QThread.TimeCriticalPriority)
         self.beginScans() 
         self.dsmThread.start.emit()#priority = QThread.TimeCriticalPriority)
      

   def dsmInit(self):
      #Configure python array to be passed by reference in shared library
      #MPERead = POINTER(c_int*8)()

      self.dsmConfig['numDAChan'] = int(self.dsmConfig['numDAChan'])

      bufSize = int(np.floor(self.dsmConfig['bufferSize']/\
         (self.dsmConfig['numDAChan']*2))*2*self.dsmConfig['numDAChan'])

      self.dsmConfig['bufferSize'] = bufSize

      SCbuffer = np.zeros(bufSize,dtype=c_int)#c_float)
      #MPE = np.zeros(8,dtype=c_int)

      Vstart = self.dsmConfig['lPstart']/20.0
      Vend = self.dsmConfig['lPend']/20.0

      DAScale = 0xFFFF/5.0

      perChBufSize = int(bufSize/int(self.dsmConfig['numDAChan']))
     
      dark = (perChBufSize*(self.dsmConfig['dark']/100))
      dark = int(np.floor(dark/(self.dsmConfig['numDAChan']*2))*\
         2*self.dsmConfig['numDAChan'])      

      #SCbuffer[0:dark*self.dsmConfig['numDAChan']] = 0

      validSpan = int(bufSize - dark*self.dsmConfig['numDAChan'])

      #print(bufSize,perChBufSize,validSpan,dark)

      ramp = np.linspace(Vstart,Vend,validSpan/self.dsmConfig['numDAChan'])
      ramp *= DAScale
      if self.dsmConfig['numDAChan'] == 1:
         SCbuffer[dark:] = ramp
      else:
         if not self.dsmConfig['laserTuning']:
            left = int(dark)#*self.dsmConfig['numDAChan'])
            right = int(perChBufSize)#int(dark*self.dsmConfig['numDAChan'] + validSpan/2)
            SCbuffer[left:right:int(self.dsmConfig['numDAChan'])] = \
               ramp[::int(self.dsmConfig['numDAChan'])]
            left = int(dark + 1 + perChBufSize)
            SCbuffer[left::int(self.dsmConfig['numDAChan'])] = \
               ramp[::int(self.dsmConfig['numDAChan'])]
         
         else:
            SCbuffer[0:perChBufSize:2] = DAScale * 2.0 
            SCbuffer[perChBufSize::2] = DAScale * 2.05
      
      scanFreq = c_float(self.dsmConfig['outRate']/\
         self.dsmConfig['bufferSize'])

      dsm.initialize(c_int(bufSize), scanFreq,\
         c_int(self.dsmConfig['laserNum']),\
         c_int(self.dsmConfig['numDAChan']),\
         c_int(self.dsmConfig['numADChan']),\
         SCbuffer.ctypes.data)
    
      self.cntrlUpdate('mpespinbox0')   
      self.cntrlUpdate('mpespinbox1')   
      self.cntrlUpdate('mpespinbox2')   
      self.cntrlUpdate('mpespinbox3')         

   def beginScans(self):
      #if ~self.dsmTimer.isActive():
      #if ~self.dsmThread.isRunning():
      if ~self.dsmThread.stopFlag:#isRunning():
         self.fileConfig['HKHeader'] = []
         self.fileConfig['HKHeader'].append(['#Housekeeping File'])
         self.fileConfig['HKHeader'].append(['#Num DA Chan: '+\
            str(self.dsmConfig['numDAChan'])])
         self.fileConfig['HKHeader'].append(['#Num AD Chan: '+\
            str(self.dsmConfig['numADChan'])])
         self.fileConfig['HKHeader'].append(['#Scan Buffer Size: '+\
            str(self.dsmConfig['bufferSize'])])
         self.fileConfig['HKHeader'].append(\
            ['Time (sec)', 'Time (usec)', '#Scans Avgd',\
            '#Scans Lost','Chan0', 'Chan1', 'Chan2', 'Chan3',\
            'Chan4', 'Chan5', 'Chan6', 'Chan7'])

         self.fileConfig['SCHeader'] = []
         self.fileConfig['SCHeader'].append(['#Spectral File'])
         self.fileConfig['SCHeader'].append(\
            ['#\tBuffer size is # of A/D conv dist evenly among #chans'])
         self.fileConfig['SCHeader'].append(\
            ['#\t(i.e. chan0_pt0.. chan1_pt0.. chan0_pt1 ...'])
         self.fileConfig['SCHeader'].append(\
            ['#Data Outrate: '+str(self.dsmConfig['outRate'])])
         self.fileConfig['SCHeader'].append(['#Num DA Chan: '+\
            str(self.dsmConfig['numDAChan'])])
         self.fileConfig['SCHeader'].append(['#Num AD Chan: '+\
            str(self.dsmConfig['numADChan'])])
         self.fileConfig['SCHeader'].append(\
            ['#Laser Number: '+str(self.dsmConfig['laserNum'])])
         self.fileConfig['SCHeader'].append(['#Scan Buffer Size: '+\
            str(self.dsmConfig['bufferSize'])])
         self.fileConfig['SCHeader'].append(\
            ['Time (sec)','Time (usec)', 'Scans ->'])

         '''
         self.fileConfig['fullScanHeader'] = []
         self.fileConfig['fullScanHeader'].append(\
            ['#Temperature Scanning Spectral File'])
         self.fileConfig['fullScanHeader'].append(\
            ['Time (sec)', 'Time (usec)', '#Scans Avgd',\
            'Temp','Settle Time', 'lPstart', 'lPend','dataRate',\
            'dark','Chan0', 'Chan1', 'Chan2', 'Chan3',\
            'Chan4', 'Chan5', 'Chan6', 'Chan7', 'Scans -> '])
         '''

         fileTime = self.getDateTime("%Y%m%d_%H%M%S")#%S") 
         #self.fileConfig['fullScan'] = 'TEMPSCAN-'+fileTime+'.csv'
         self.fileConfig['HK'] = 'Data/CLIH-'+fileTime+'_HK.csv'
         self.fileConfig['SC'] = 'Data/CLIH-'+fileTime+'_SC.csv'

         #May be important to add try routine for appending.

         self.HKfile = open(self.fileConfig['basePath']+\
            self.fileConfig['HK'],'w',newline='')
         for row in self.fileConfig['HKHeader']:
            csv.writer(self.HKfile).writerow(row)

         self.SCfile = open(self.fileConfig['basePath']+\
            self.fileConfig['SC'],'w',newline='')
         for row in self.fileConfig['SCHeader']:
            csv.writer(self.SCfile).writerow(row)

         print('success?')

         '''
         self.fullScanFile = open(self.fileConfig['basePath']+\
            self.fileConfig['fullScan'],'w',newline='')
         for row in self.fileConfig['fullScanHeader']:
            csv.writer(self.fullScanFile).writerow(row)
         '''

      #self.dsmTimer.start(1)
      self.dsmThread.dsmConfig = self.dsmConfig
      self.dsmThread.wvScanConfig = self.wvScanConfig
      #self.dsmThread.start()
      self.dsmThread.start.emit()
     
   def mpeConvert(self,voltages = []):
      voltages = [float(x) for x in voltages]
      for i in range(2):
         tmp = voltages[i];
         tmp = tmp*10000.0/(5.0 - tmp)
         tmp = 0.001128 + 0.0002345*np.log(tmp) + 0.0000000873*pow(np.log(tmp),3)
         tmp = 1.0/tmp - 273.15;
         voltages[i] = tmp
      
      tmp = voltages[2]
      tmp = 26700.0*((5.0/tmp) - 1)
      voltages[2] = 1.0/(1/298.15 + 1/3810.0*np.log(tmp/30000.0))-273.15
      
      voltages[3] = voltages[3]*222.38935 + 114.06569      

      return voltages       

   @QtCore.pyqtSlot(object,object,object)
   def dataSave(self,saveCode,prefix,array):
      suppressPlot = False#True
      prefix = list(prefix)
      array = list(array)
      #startTime = timeit.default_timer()
      if saveCode == 0: fileHandle = self.HKfile
      if saveCode == 1: fileHandle = self.SCfile
      if saveCode == 2: fileHandle = self.fullScanFile
      if saveCode == 3: 
         self.runTempScans(True)
         return

      if saveCode == 0:
         array = self.mpeConvert((array)) 
         if not suppressPlot:
            for i in range(4):
               self.findChild(QtWidgets.QLineEdit,'mpeAD'+str(i)).\
                  setText('{:.3f}'.format(array[i]))
            self.findChild(QLineEdit,'avgCtr').setText(\
               "{:.0f}".format(prefix[2]))
            self.findChild(QLineEdit,'lossCtr').setText(\
               "{:.0f}".format(prefix[3]))
 
      if saveCode == 2: 
         bufSize = int(self.dsmConfig['bufferSize'])
         array[-bufSize-8:-bufSize] = self.mpeConvert(\
            (array[-bufSize-8:-bufSize]))
         if not suppressPlot:
            for i in range(4):
               self.findChild(QtWidgets.QLineEdit,'mpeAD'+str(i)).\
                  setText('{:.3f}'.format(array[-bufSize-8+i]))
       
      csv.writer(fileHandle,quoting=csv.QUOTE_NONE).\
         writerow(['{:.0f}'.format(int(x)) for x in prefix] + ['{:.7g}'.format(x) for x in array])
      #fastcsv.Writer(fileHandle, quote = csv.QUOTE_NONE).\
      #   writerow(['{:.0f}'.format(int(x)) for x in prefix] + ['{:.7g}'.format(x) for x in array])

      if saveCode == 2:
         array = array[-bufSize:] 

      #if saveCode == 2: array = array[-bufSize:]
   
      if not suppressPlot:
         if saveCode >= 1: 
            self.plot2.setGeometry(self.plot.plotItem.vb.sceneBoundingRect())
            self.plot2.linkedViewChanged(self.plot.plotItem.vb,\
               self.plot2.XAxis)

            self.plot.enableAutoRange(axis=pg.ViewBox.XAxis)
            self.plot.setMouseEnabled(x=False,y=False)
        
            #self.plot.showAxis('right')
            self.plot.getAxis('right').setLabel('Voltage (V)')

            if self.dsmConfig['numDAChan'] == 1:
               self.plot2.clear()
               self.plot.hideAxis('right')
               self.plot.plot(range(len(array))[:],\
                  array[:], clear = True, pen = pg.mkPen(color=\
                  (255,255,255), width = 2))
            else:
               self.plot2.clear()
               self.plot.showAxis('right')
               half = int(len(array)/2)
               self.plot.plot(range(half)[:half],\
                  array[:half], clear = True, pen = pg.mkPen(color=\
                  (255,255,255), width = 2))
               self.plot2.addItem(pg.PlotCurveItem(\
                  np.array(range(half)),np.array(array[half:]),\
                  clear = True, pen = pg.mkPen(color = \
                  (255,125,125), width = 2)))

         #self.plot2.clear()
         #self.plot2.addItem(pg.PlotCurveItem(\
         #   np.array(range(self.dsmConfig['bufferSize'])[0::12]),\
         #   np.array(array[0::12]),\
         #   clear = True, pen = pg.mkPen(color=(255,255,255),\
         #   width = 1)))

         #app.processEvents()
 
         #C = pg.hsvColor(3/5%1,alpha=1.0)
         #pen = pg.mkPen(color=C,width=2)
         #self.plotDataItem.setData(np.arange(0,\
         #   self.dsmConfig['bufferSize'])[0::24],array[0::24])#,\
         
         #   self.plotDataItem.setData(np.arange(0,\
         #      self.dsmConfig['bufferSize']),array)
         #C = pg.hsvColor(time.time()/5%1,alpha=1.0)
         #self.plotDataItem = 
         #self.plotDataItem.setData(np.arange(0,\
         #   self.dsmConfig['bufferSize']),array,\
         #   pen=pen,symbolBrush=(255,0,0),\
         #   symbolSize=2,symbolPen=None)
         #self.plot.plot(range(0,self.dsmConfig['bufferSize'])[0::24],\
         #   array[0::24],clear=True,pen=None,symbolBrush=(255,0,0),\
         #   symbolSize=2,symbolPen=None)

      #print(timeit.default_timer() - startTime)


   def dsmStop(self):
      app.processEvents()
      #print("I am doing something?")
      try: 
         self.HKfile.close()
         self.SCfile.close()
      except: print("Failed to HK/SC files")
      try:
         self.fullScanFile.close()
      except: print("Failed to close tempscan file")

      self.dsmThread.stop()   
      #self.dsmThread.stop.emit()   
      #self.dsmTimer.stop()


   def setLaserTemp(self,laserNum, temp):
      #temp = temp + 273.15
      x = 1.0/(0.0000000873)*(0.001128 - 1.0/(temp+273.15))
      y = np.sqrt(pow(0.0002345/(3.0*0.0000000873),3) + pow(x/2.0,2));
      setpt = np.exp((np.cbrt(y - x/2.0) - np.cbrt(y + x/2.0)))
      setpt = 16.0308*(setpt - 10000.0)/(setpt + 10000.0)
      if (setpt < 0.0): setpt = 0.0
      if (setpt > 5.0): setpt = 5.0
      if ( laserNum > 0 ): dsm.writeMPEvoltage(c_float(setpt), c_int(laserNum - 1))


   #Required intercept for close program dialog
   def closeEvent(self, event):
      result = QMessageBox.warning(ui, 'WARNING',"Are you sure you want to close the program?", QMessageBox.Yes, QMessageBox.No)
      event.ignore()
      if result == QMessageBox.Yes:
         #self.closeTrigger = True
         self.dsmStop()
         dsm.interface_close()
         event.accept()

class DSMLoop(QObject):#QThread):
   start = pyqtSignal()
   stop = pyqtSignal()
   def __init__(self,conf,wvconf,parent=None):
      super(DSMLoop,self).__init__(parent)
      self.dsmConfig = conf
      self.wvScanConfig = wvconf
      self.stopFlag = False
      
      #self.dsmTimer = QTimer()
      #self.dsmTimer.timeout.connect(self.dsmUpdate)
      self.start.connect(self.run)

   #def run(self):
   #  self.dsmTimer.start(1)  
 
   #def dsmUpdate(self):
   @QtCore.pyqtSlot()
   def run(self):
      #print( timeit.default_timer() - startTime)
      #MPEaccum = (c_float*8)()
      MPE = np.zeros(8,dtype=c_int)
      MPEaccum = np.zeros(8,dtype=c_float)

      MPEprefix = np.zeros(8,dtype='int')
      SCprefix = np.zeros(2,dtype='int')

      SC = np.zeros(self.dsmConfig['bufferSize'],dtype=c_int)
      SCaccum = np.zeros(self.dsmConfig['bufferSize'],dtype=c_float) 
      SCcopy = np.zeros(self.dsmConfig['bufferSize'],dtype=c_int)
      #Get A/D Conversion parameters

      fifoCtr= 0; lossCtr = 0; avgCtr = 0

      tv1 = time.time()
      oldTimeSegment = int(np.floor((tv1%1)/(1.0/\
         float(self.dsmConfig['saveRate']))))

      tempSteps = np.linspace(self.wvScanConfig['startTemp'],\
         self.wvScanConfig['endTemp'],self.wvScanConfig['tempSteps'])
      settleTime = self.wvScanConfig['settleTime']
      avgPerStep = self.wvScanConfig['avgPerStep']
      tempIndex = 0
      if self.dsmConfig['spectralScan']:
         ui.tempChange.emit(self.dsmConfig['laserNum'],\
            tempSteps[tempIndex])
         if self.dsmConfig['numDAChan'] == 2:
            ui.tempChange.emit(self.dsmConfig['laserNum']+1,\
               tempSteps[tempIndex])
         tv2 = time.time()
      #else:
      dark = (self.dsmConfig['bufferSize']*\
         (self.dsmConfig['dark']/100))
      dark = int(np.floor(dark/(self.dsmConfig['numDAChan']*2))*\
         2*self.dsmConfig['numDAChan'])      
   
         #Need start temp value, end temp value, #divisions
         #  number of spectra per value, settling time

      self.stopFlag = False
         
      #startTime = timeit.default_timer()
      while not self.stopFlag:
         
         numCon = dsm.readBuffer( SC.ctypes.data )#dsm.analogIntStatus()#self.FIFOCounter)
         #numMPE = dsm.statusMPE()
       
         if(numCon <= fifoCtr): 
             #time.sleep(0.001)#5)
            continue
         
         while np.allclose(SCcopy, SC, ):#np.array_equal(SCcopy,SC):
            numCon = dsm.readBuffer( SC.ctypes.data)
            #print(numCon)
            #time.sleep(0.001)
         np.copyto(SCcopy,SC)#continue
         #time.sleep(0.005)
         
         dsm.MPEreadBuffer( MPE.ctypes.data )
         
         #null = dsm.readBuffer( SC.ctypes.data )

         #Check to see if settle time is adequate for spectral scans
         if self.dsmConfig['spectralScan']:
            if (time.time() - tv2) < self.wvScanConfig['settleTime']:
               continue
         
         
         #numCon = dsm.readBuffer( SC.ctypes.data )
         lossCtr += numCon - fifoCtr - 1
         fifoCtr = numCon
         
         #print(numCon)#, null)
         #continue
            
         '''
         try:
            if np.array_equal(SCcopy,SC):#(oldSC == SC).all():
               lossCtr += 1
               #print('Discarding sample!')
               continue
            np.copyto(SCcopy,SC)
         except: np.copyto(SCcopy,SC)
         '''

         #lossCtr += (int(numCon) - int(fifoCtr) - 1)
         #Added second loss increment to see
         #lossCtr += (int(fifoCtr) - int(numCon))
 

         MPEaccum += (MPE); SCaccum += (SC)
         avgCtr += 1
         #print(avgCtr,lossCtr) 
         #continue
         #print(SC[150],SCaccum[150]*20.0/(65536.0*float(avgCtr)))

         if self.dsmConfig['spectralScan']:
            #Checks to see if adequate average has been passed....
            if avgCtr % 25 == 0: 
               print("Temp: ",tempSteps[tempIndex],", avgCtr: ",float(avgCtr))
            if avgCtr < self.wvScanConfig['avgPerStep']: continue


            #Form prefix....
            wvScanPrefix = [np.floor(tv1), (tv1%1)*1000000, avgCtr, \
               tempSteps[tempIndex], self.wvScanConfig['settleTime'],\
               self.dsmConfig['lPstart'], self.dsmConfig['lPend'],\
               self.dsmConfig['outRate'],dark]

            #Send save signal for spectral scan, index 2
            ui.saveSignal.emit(2,wvScanPrefix[:2],wvScanPrefix[2:] + \
               list(MPEaccum*10.0/(65536.0*avgCtr))+\
               list(SCaccum*20.0/(65536.0*avgCtr)))

            #get new tv2
            tv2 = time.time()
            #Try to change temp, if fails, we are done
            try:
               tempIndex += 1
               ui.tempChange.emit(self.dsmConfig['laserNum'],\
                  tempSteps[tempIndex])
               if self.dsmConfig['numDAChan'] == 2:
                  ui.tempChange.emit(self.dsmConfig['laserNum']+1,\
                     tempSteps[tempIndex])
                  
            except:
               tempIndex = 0
               ui.saveSignal.emit(3,[],[]) 
               self.dsmConfig['spectralScan'] = False

         else:
            tv2 = time.time()
            newTimeSegment = int(np.floor((tv2 % 1.0)/\
               (1.0/float(self.dsmConfig['saveRate']))))
         
            #Checks to see if the new time segment is over one seg past old
            if( np.floor(tv2) + 1.0/float(self.dsmConfig['saveRate']) * \
               float(newTimeSegment) <= np.floor(tv1) + \
               1.0/float(self.dsmConfig['saveRate']) * \
               float(oldTimeSegment) ):
                  continue
            #print("Avg'd: ",avgCtr,", Lost: ",lossCtr, "numCon: ",\
            #   numCon, ", MPECon: ", numMPE) 
            #print("Time Segment: "+str(newTimeSegment+1) + " out of "+str(self.dsmConfig['saveRate']))

            #MPEprefix = [np.floor(tv2), (tv2%1)*1000000, avgCtr, lossCtr]# + list(self.MPEReadAccum
            #SCprefix = np.array([np.floor(tv2), (tv2%1)*1000000])# + list(self.MPEReadAccum)
            SCprefix[0] = np.floor(tv1)
            SCprefix[1] = (tv1%2)*1000000           

            MPEprefix[0] = np.floor(tv1)
            MPEprefix[1] = (tv1%2)*1000000
            MPEprefix[2] = avgCtr
            MPEprefix[3] = lossCtr
            MPEprefix[4] = self.dsmConfig['lPstart']
            MPEprefix[5] = self.dsmConfig['lPend']
            MPEprefix[6] = self.dsmConfig['outRate']
            MPEprefix[7] = dark 
            #MPEprefix = np.array([np.floor(tv1), (tv1%1)*1000000, avgCtr, \
            #   lossCtr, self.dsmConfig['lPstart'], \
            #   self.dsmConfig['lPend'],\
            #   self.dsmConfig['outRate'],dark])

            oldTimeSegment = newTimeSegment 
         
            if( avgCtr > 0 ):
               ui.saveSignal.emit(0,MPEprefix,\
                  (MPEaccum*10.0/(65536.0*avgCtr)))
               ui.saveSignal.emit(1,SCprefix,\
                  (SCaccum*20.0/(65536.0*avgCtr)))
               #dsm.analogConvert(SCaccum)
               #dsm.MPEanalogConvert( MPEaccum )
            else:
               ui.saveSignal.emit(0,MPEprefix,(MPEaccum*0 - 9999))
               ui.saveSignal.emit(1,SCprefix,(SCaccum*0 - 9999))
     
         #print(avgCtr,lossCtr) 
         avgCtr = 0; lossCtr = 0
         SCaccum *= 0; MPEaccum *= 0
         tv1 = tv2
   
   #@QtCore.pyqtSlot()
   def stop(self):
      self.stopFlag = True
      #self.dsmTimer.stop()
   #def __del__(self):
   #   self.dsmTimer.stop()

   def __del__(self):
      self.quit()
      self.wait()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ui = Ui_MainWindow()
   ui.setWindowTitle("Cloud Isotope Instrument")

   ui.show()

   sys.exit(app.exec_())








