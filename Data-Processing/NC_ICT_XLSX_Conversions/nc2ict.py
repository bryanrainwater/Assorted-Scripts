#ICARTT MACRO	

from netCDF4 import Dataset
import os
import sys
import numpy as np
import time

import csv

import copy

#from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog#QInputDialog, QLineEdit, QFileDialog
#from PyQt5.QtGui import QIcon

import tkinter as tk
from tkinter import filedialog


class Process:#App(QWidget):
 
	def __init__(self):
		super().__init__()
		#self.title = 'PyQt5 file dialogs - pythonspot.com'
		#self.left = 50
		#self.top = 50
		#self.width = 640
		#self.height = 480
		#self.initUI()
		self.runProcessing()
 
	#def initUI(self):
	#	#self.setWindowTitle(self.title)
	#	#self.setGeometry(self.left, self.top, self.width, self.height)
 
	#	#self.openFileNameDialog()
	#	#self.openFileNamesDialog()
	#	#self.saveFileDialog()

	#	#self.show()
	#	#sys.exit(app.exec_())
		
	def runProcessing(self):

		#Load NetCDF file
		#options = QFileDialog.Options()
		#defaultDir = os.path.expanduser('~').replace('\\','/')
		#fileName, _ = QFileDialog.getOpenFileName(self, "Select NetCDF File", './', "NetCDF Files (*.nc);;All Files (*)", options = options)
		fileName = filedialog.askopenfilename()
		if fileName:
			print(fileName)
			dataset = Dataset(fileName)
		else: return

		#File Names

		dataStruct  = {}
		dataStructDesc = {}
		dataStructUnits = {}
		dataStructFillValue = {}

		#Parameter Keys to parse from netcdf
		#ncParamKeys = np.array([['TASX','Total Airspeed','m/s'],['ATX','Ambient Air Temperature','C']])

		ncVariableNames = np.array(['CVINLET','CVFXFLOWS','CVFX5','CVFX6','CVFX7','CVCWCC','CVRAD','CVCFACT','CONCU_CVIU'])
		ncVariableDesc = np.array(['-','-','-','-','-','-','-','-','-'])
		
		timestamp = (dataset.variables['Time'][:])
		outTime = str(dataset.variables['Time'].units)

		outTime = outTime.split('seconds since ')[1]
		outTime = outTime.split(' ')[0]
		dateout = outTime.replace('-','')
		print(dateout)
		input('wait')
		
		for key, desc in zip(ncVariableNames,ncVariableDesc):#extraParamKeys:
			#print(key)
			try: dataStruct[key] = dataset.variables[key][:,0]#dataset.variables[key[0]][:]
			except: dataStruct[key] = dataset.variables[key][:]
			try: 
				dataStruct[key]
				dataStructDesc[key] = str(dataset.variables[key].long_name)
				if desc == '-':	dataStructUnits[key] = str(dataset.variables[key].units)#key[2]
				else: dataStructUnits[key] = desc
				dataStructFillValue[key] = dataset.variables[key]._FillValue
				#extraParams.append(dataset.variables[key][:])
			except: 
				keysToRemove.append(key)
				
		dataStruct['CONCU_CVIU_SDI'] = copy.deepcopy(dataStruct['CONCU_CVIU'])
		dataStructDesc['CONCU_CVIU_SDI'] = 'CVI UHSAS while on SDI'
		dataStructUnits['CONCU_CVIU_SDI'] = dataStructUnits['CONCU_CVIU']
		dataStructFillValue['CONU_CVIU_SDI'] = dataStructFillValue['CONCU_CVIU']
		
		for key in dataStruct:
			dataStruct[key] = np.array(dataStruct[key])
				
		#############################################
		#VERIFY TIME DOMAIN IS EVENLY SPACED
		#ONLY NEEDED WHEN CONFIGURED FOR NON NC FILES
		#############################################
		cviFile = filedialog.askopenfilename()
		if fileName:
			print(fileName)
			cvireader = csv.reader(open(cviFile, "r"), delimiter=",")
			cviheader = next(cvireader, None)
			x = list(cvireader)
			cvidata = np.array(x).astype("float")
			
			cviTime = np.floor(cvidata[:,0])
		
			fillRow = cvidata[0,:]
			fillRow[1:] = -9999
		
			minDiff =  int(np.abs(min(timestamp) - min(cviTime)))
			maxDiff = int(np.abs(max(timestamp) - max(cviTime)))
		
			for i in range(minDiff):
				np.insert(cvidata, 0, fillRow, 0)
				cvidata[0,0] = cvidata[1,0] - 1.0

			for i in range(maxDiff):
				cvidata = np.vstack((cvidata,fillRow))
				cvidata[-1,0] = cvidata[-2,0] + 1.0

		#############################################
		#############################################
		#############################################
		#############################################						
			
		###ADD UHSAS Time lag dependence............#	
			
		#RF01 through RF03, 3 way valve closed during SDI mode
		#	i.e. only ambient data for Impactor
		
		#For RF04, when UHSAS pressure drops ~50 mbar below
		#	CVPCN, set flag to 2. recalculate all parameters.
	
		#SDI mode was unused on RF03?
		
		#SO, treat RF03, 5, .... all the same.
		#	in that when flag = 0, concu_cviu is populated, 
		#	and concu_cviu_sdi is nulled, opposite when flag = 2
		
		#For RF01 through RF03, when flag = 2, all are nulled.
		#	no need to recalculate cvcfact, cvrad, cvcwc
		
			
			
		#Corrections for RF01 - RF04
		if dateout == '20180725' or dateout == '20180726':#RF01 and RF02 #or dateout == '20180730':
			#Load in Corrected files for the various data.
			dataStruct['CVINLET'] = cvidata[:,1]
			dataStruct['CVFXFLOWS'] = cvidata[:,2]
			dataStruct['CVFX5'] = cvidata[:,32]
			dataStruct['CVFX6'] = cvidata[:,33]
			dataStruct['CVFX7'] = cvidata[:,34]
			dataStruct['CVRAD'] = cvidata[:,39]
			dataStruct['CVRHOO_TDL'] = cvidata[:,37]
			dataStruct['CVCFACT'] = cvidata[:,45]
			
			for key in dataStruct:
				if key != 'Time' and if 'CONCU' not in key and if key != 'CVINLET':
					dataStruct['key'][dataStruct['CVINLET'] == 2] = -9999.
				else:
					dataStruct['CONCU_CVIU_SDI'][dataStruct['CVINLET'] == 0] = -9999
					dataStruct['CONCU_CVIU'][dataStruct['CVINLET'] == 2] = -9999			
		elif dateout == '20180731': #RF04
			print('Second Correction')
			
		variableNames = []
		variableDesc = []
		variableUnits = []
		for key, value in dataStruct.items():
			variableNames.append(key)
			variableDesc.append(dataStructDesc[key])
			variableUnits.append(dataStructUnits[key])

		outData = np.c_[timestamp]#fileTime]
		for key in dataStruct:
			outData = np.c_[outData, dataStruct[key]]
					
			
		outData[outData == -32767] = -9999

		outName = self.namingConvention(fileName, dateout)	
		self.saveFormat(dateout, outName, outData, variableNames, variableDesc, variableUnits)	
	
	def namingConvention(self, inputFile = '', datestring = '', extraComment = ''):
		fileNameInfo = './missionInfo.txt'
		outName = os.path.dirname(inputFile)
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
			outName += extraComment
			outName += '.ict'
	
		return outName	
		#self.VMRFileName = outName
	

	def saveFormat(self, dateout = '', outName = '', outData = [], variableNames = [], variableDesc = [], variableUnits = []):
			packagedFileName = './headerFormat.txt'
		
			if variableUnits == []:
				variableUnits = ['unit']*len(variableNames)
				
			timestamp = time.strftime("%Y%m%d")
			#outName = (''.join(outName.split('packaged_')[:-1])+'packaged_'+str(timestamp)+'.csv')
			#datestring = ''.join(''.join(outName.split('CLH2-')[-1:]).split('_')[0])
			datestring = ''.join(''.join(outName.split('-')[-1:]).split('_')[0])
			dateout = str(dateout[0:4]) + ', ' + str(dateout[4:6]) + ', ' + str(dateout[6:8]) + \
				', ' + str(timestamp[0:4]) + ', ' + str(timestamp[4:6]) + ', ' + str(timestamp[6:8])	
				
			###Write header:::
			header = []
			counter = 0
			with open(outName, 'w', newline='') as outFile:
				with open(packagedFileName, 'r') as headerFile:
					for i, line in enumerate(headerFile):#line = parFile.readLine()
						try:
							line = line.replace('\n','')
							line = line.replace('\r','')
							if i <= 15:
								line = ':'.join(line.split(':')[1:])
								line = line.lstrip()
								if len(line) == 0: continue
								if i == 6: 
									counter += 1
									header.append([dateout])
								if i == 9 or i == 10:
									line = [line]*len(variableNames)
									header.append([', '.join(line)])
									continue
								if i == 11:
									for var in zip(variableNames,variableUnits, variableDesc):
										header.append([var[0]+', '+var[1]+ ', '+var[2]])
										counter += 1
									continue
							header.append([line])
						except: pass

				header.append([', '.join(['Start_UTC'] + variableNames)])
			
				header[0][0] = str(int(len(header))) + ', ' + header[0][0]

				header[9][0] = str(int(len(variableNames)))

				header[12+counter][0] = str(int(len(header[13+counter:])))

				for line in header:
					outFile.write(line[0])
					outFile.write('\n')

				for row in outData:
					#tmp = '{:11d}'.format(int(row[0]))+','
					tmp = '{:.3f}'.format((row[0]))+','
					row = row[1:]
					#tmp+=','.join(["{:11.6f}".format(x) for x in row])
					tmp+=','.join(["{:.6e}".format(x) for x in row])
					tmp+='\n'
					outFile.write(tmp)


			#icartt file name is of the following format:
			#	dataID_locationID_YYYYMMDD[hh[mm[ss]]]_R#[_L#][_V#][_comments].ict
			#example:
			#	ORCAS-CUTOTAL-H2O_GV_2018MMDD_R1_FF01.ict
	
			#icart required headers from format file.
	
			return header
		
		
root = tk.Tk()
#root.withdraw()		
		
Process()
		
'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
'''